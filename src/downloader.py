import os
import subprocess
import json
import time
import logging
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .config import (
    FORMATS, MAX_RETRIES, RETRY_DELAY, MAX_CONCURRENT_DOWNLOADS,
    DOWNLOADS_DIR, CHUNK_SIZE, DOWNLOAD_TIMEOUT, MAX_DOWNLOAD_SIZE,
    PREVIEW_DURATION
)
from .utils import (
    validate_url, check_disk_space, sanitize_filename,
    ValidationError
)

class DownloadError(Exception):
    """Exceção customizada para erros de download."""
    pass

@dataclass
class DownloadTask:
    """Representa uma tarefa de download."""
    url: str
    output_path: Path
    format_options: Dict
    callback: Optional[Callable] = None
    process: Optional[subprocess.Popen] = None
    status: str = "pending"
    progress: float = 0.0
    error: Optional[str] = None

class MediaDownloader:
    def __init__(self):
        self.setup_logging()
        self.yt_dlp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "yt-dlp")
        self.ensure_directories()
        self.active_downloads: Dict[str, DownloadTask] = {}
        self.download_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS)
        self._stop_event = threading.Event()

    def setup_logging(self):
        """Configura o sistema de logging."""
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(DOWNLOADS_DIR, "downloader.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def ensure_directories(self):
        """Garante que os diretórios necessários existam."""
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    def get_media_info(self, url: str) -> Dict:
        """Obtém informações sobre o vídeo/playlist."""
        try:
            validate_url(url)
            cmd = [
                self.yt_dlp_path,
                "--dump-json",
                "--flat-playlist",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            return info
        except subprocess.CalledProcessError as e:
            raise DownloadError(f"Erro ao obter informações: {str(e)}")
        except json.JSONDecodeError as e:
            raise DownloadError(f"Erro ao decodificar informações: {str(e)}")

    def download_media(self, url: str, output_dir: Path, format_options: Dict, callback: Optional[Callable] = None) -> None:
        """Baixa mídia do YouTube."""
        try:
            validate_url(url)
            check_disk_space(output_dir)

            # Cria tarefa de download
            task = DownloadTask(
                url=url,
                output_path=output_dir,
                format_options=format_options,
                callback=callback
            )

            # Adiciona à fila
            self.download_queue.put(task)
            self.active_downloads[url] = task

            # Inicia o download
            self._process_download(task)

        except (ValidationError, DownloadError) as e:
            raise DownloadError(str(e))

    def _process_download(self, task: DownloadTask) -> None:
        """Processa uma tarefa de download."""
        try:
            # Prepara comando yt-dlp
            cmd = [
                self.yt_dlp_path,
                "--format", task.format_options["format"],
                "--output", str(task.output_path / "%(title)s.%(ext)s"),
                task.url
            ]

            if "quality" in task.format_options:
                cmd.extend(["--audio-quality", task.format_options["quality"]])

            # Inicia processo
            task.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitora progresso
            while task.process.poll() is None:
                if self._stop_event.is_set():
                    task.process.terminate()
                    break

                if task.callback:
                    task.callback(task.progress, "Downloading...")

                time.sleep(0.1)

            # Verifica resultado
            if task.process.returncode == 0:
                task.status = "completed"
                if task.callback:
                    task.callback(100, "Download completed")
            else:
                task.status = "failed"
                task.error = task.process.stderr.read() if task.process.stderr else "Unknown error"
                if task.callback:
                    task.callback(0, f"Download failed: {task.error}")

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            if task.callback:
                task.callback(0, f"Download failed: {str(e)}")

        finally:
            if task.url in self.active_downloads:
                del self.active_downloads[task.url]

    def preview_media(self, url: str, format_options: Dict) -> Optional[Path]:
        """Gera uma prévia da mídia."""
        try:
            validate_url(url)
            preview_dir = DOWNLOADS_DIR / "previews"
            os.makedirs(preview_dir, exist_ok=True)

            # Gera nome único para prévia
            preview_name = f"preview_{int(time.time())}"
            preview_path = preview_dir / f"{preview_name}.{format_options['format']}"

            # Prepara comando yt-dlp com limite de duração
            cmd = [
                self.yt_dlp_path,
                "--format", format_options["format"],
                "--output", str(preview_path),
                "--postprocessor-args", f"-t {PREVIEW_DURATION}",
                url
            ]

            if "quality" in format_options:
                cmd.extend(["--audio-quality", format_options["quality"]])

            # Executa comando
            process = subprocess.Popen(cmd)
            process.wait()

            if process.returncode == 0:
                return preview_path
            return None

        except Exception as e:
            logging.error(f"Erro ao gerar prévia: {str(e)}")
            return None

    def cancel_download(self, url: str) -> None:
        """Cancela um download em andamento."""
        if url in self.active_downloads:
            task = self.active_downloads[url]
            if task.process and task.process.poll() is None:
                task.process.terminate()
                task.status = "cancelled"
                if task.callback:
                    task.callback(0, "Download cancelled")

    def cleanup(self) -> None:
        """Limpa recursos do downloader."""
        self._stop_event.set()
        for task in self.active_downloads.values():
            if task.process and task.process.poll() is None:
                task.process.terminate()
        self.executor.shutdown(wait=False)

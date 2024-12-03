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

from config import (
    FORMATS, MAX_RETRIES, RETRY_DELAY, MAX_CONCURRENT_DOWNLOADS,
    DOWNLOADS_DIR, CHUNK_SIZE, DOWNLOAD_TIMEOUT, MAX_DOWNLOAD_SIZE,
    PREVIEW_DURATION
)
from utils import (
    validate_url, check_disk_space, sanitize_filename,
    cache_manager, download_history, setup_logger,
    ValidationError
)

@dataclass
class DownloadTask:
    """Representa uma tarefa de download."""
    url: str
    output_path: Path
    format_info: Dict
    callback: Optional[Callable] = None
    preview_only: bool = False

class DownloadError(Exception):
    """Exceção customizada para erros de download."""
    pass

class MediaDownloader:
    def __init__(self):
        self.logger = setup_logger('downloader')
        self.download_queue = queue.Queue()
        self.active_downloads = {}
        self.cancel_events = {}
        self._setup_worker_threads()

    def _setup_worker_threads(self):
        """Configura threads trabalhadoras para downloads."""
        self.workers = []
        for _ in range(MAX_CONCURRENT_DOWNLOADS):
            worker = threading.Thread(target=self._download_worker, daemon=True)
            worker.start()
            self.workers.append(worker)

    def _download_worker(self):
        """Thread trabalhadora para processar downloads da fila."""
        while True:
            try:
                task = self.download_queue.get()
                if task is None:
                    break
                
                download_id = id(task)
                self.cancel_events[download_id] = threading.Event()
                
                try:
                    self._process_download_task(task, download_id)
                except Exception as e:
                    self.logger.error(f"Erro no download {download_id}: {str(e)}")
                finally:
                    self.download_queue.task_done()
                    self.active_downloads.pop(download_id, None)
                    self.cancel_events.pop(download_id, None)
            
            except Exception as e:
                self.logger.error(f"Erro na thread trabalhadora: {str(e)}")

    def _process_download_task(self, task: DownloadTask, download_id: int):
        """Processa uma tarefa de download individual."""
        try:
            # Configurar comando base
            cmd = [
                "yt-dlp",
                "--output", str(task.output_path),
                "--socket-timeout", str(DOWNLOAD_TIMEOUT),
                "--limit-rate", f"{CHUNK_SIZE}K"
            ]

            if task.preview_only:
                cmd.extend([
                    "--download-sections", f"*0:{PREVIEW_DURATION}",
                    "--force-overwrites"
                ])

            if task.format_info["format"] == "mp3":
                cmd.extend([
                    "-x",
                    "--audio-format", "mp3",
                    "--audio-quality", task.format_info["quality"]
                ])
            else:
                cmd.extend([
                    "-f", f"bestvideo[height<={task.format_info['quality']}]+bestaudio",
                    "--merge-output-format", "mp4"
                ])

            cmd.append(task.url)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.active_downloads[download_id] = process

            while True:
                if self.cancel_events[download_id].is_set():
                    process.terminate()
                    raise DownloadError("Download cancelado pelo usuário")

                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break

                if task.callback and "[download]" in line:
                    task.callback(line)

            if process.returncode != 0:
                raise DownloadError(f"Download falhou com código {process.returncode}")

            # Registrar download bem-sucedido
            if not task.preview_only:
                download_history.add_entry(
                    task.url,
                    task.format_info["format"],
                    task.format_info["quality"],
                    "completed"
                )

        except Exception as e:
            if not task.preview_only:
                download_history.add_entry(
                    task.url,
                    task.format_info["format"],
                    task.format_info["quality"],
                    f"failed: {str(e)}"
                )
            raise

    def get_media_info(self, url: str) -> Dict:
        """Obtém informações sobre o vídeo/playlist."""
        try:
            # Tentar obter do cache primeiro
            cached_info = cache_manager.get(url)
            if cached_info:
                return cached_info

            validate_url(url)
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)

            # Salvar no cache
            cache_manager.set(url, info)
            return info

        except subprocess.CalledProcessError as e:
            raise DownloadError(f"Erro ao obter informações: {str(e)}")
        except json.JSONDecodeError as e:
            raise DownloadError(f"Erro ao processar informações: {str(e)}")

    def preview_media(self, url: str, format_info: Dict, callback: Optional[Callable] = None) -> Path:
        """Gera uma prévia do vídeo/áudio."""
        try:
            info = self.get_media_info(url)
            preview_filename = f"preview_{sanitize_filename(info['title'])}"
            preview_path = DOWNLOADS_DIR / "previews" / preview_filename

            task = DownloadTask(
                url=url,
                output_path=preview_path,
                format_info=format_info,
                callback=callback,
                preview_only=True
            )

            self.download_queue.put(task)
            return preview_path

        except Exception as e:
            raise DownloadError(f"Erro ao gerar prévia: {str(e)}")

    def download_media(self, url: str, output_dir: Path, format_info: Dict,
                      callback: Optional[Callable] = None) -> None:
        """Inicia o download de mídia."""
        try:
            validate_url(url)
            check_disk_space(output_dir)

            info = self.get_media_info(url)
            filename = sanitize_filename(info['title'])
            output_path = output_dir / filename

            task = DownloadTask(
                url=url,
                output_path=output_path,
                format_info=format_info,
                callback=callback
            )

            self.download_queue.put(task)

        except Exception as e:
            raise DownloadError(f"Erro ao iniciar download: {str(e)}")

    def cancel_download(self, download_id: int):
        """Cancela um download em andamento."""
        if download_id in self.cancel_events:
            self.cancel_events[download_id].set()

    def get_active_downloads(self) -> List[Dict]:
        """Retorna informações sobre downloads ativos."""
        return [
            {
                "id": download_id,
                "status": "downloading" if process.poll() is None else "finishing"
            }
            for download_id, process in self.active_downloads.items()
        ]

    def cleanup(self):
        """Limpa recursos e encerra threads trabalhadoras."""
        # Sinalizar para as threads pararem
        for _ in self.workers:
            self.download_queue.put(None)
        
        # Esperar todas as threads terminarem
        for worker in self.workers:
            worker.join()
        
        # Cancelar downloads ativos
        for download_id in list(self.active_downloads.keys()):
            self.cancel_download(download_id)

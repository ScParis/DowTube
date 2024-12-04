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
        """Função principal da thread trabalhadora."""
        while True:
            try:
                task = self.download_queue.get()
                if task is None:
                    break

                # Configura evento de cancelamento
                cancel_event = threading.Event()
                self.cancel_events[task.url] = cancel_event

                try:
                    self._process_download(task, cancel_event)
                except Exception as e:
                    self.logger.error(f"Erro no download de {task.url}: {str(e)}")
                    if task.callback:
                        task.callback(False, str(e))
                finally:
                    self.download_queue.task_done()
                    if task.url in self.cancel_events:
                        del self.cancel_events[task.url]

            except Exception as e:
                self.logger.error(f"Erro na thread trabalhadora: {str(e)}")

    @cache_manager
    def get_video_info(self, url: str) -> Dict:
        """Obtém informações do vídeo."""
        try:
            validate_url(url)
            
            # Usa yt-dlp para obter informações
            cmd = ['yt-dlp', '-J', url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise DownloadError(f"Erro ao obter informações: {result.stderr}")
            
            return json.loads(result.stdout)
        
        except Exception as e:
            raise DownloadError(f"Erro ao obter informações do vídeo: {str(e)}")

    @download_history
    def download(self, url: str, format_info: Dict, output_path: Optional[Path] = None,
                callback: Optional[Callable] = None, preview: bool = False) -> bool:
        """Inicia o download de uma mídia."""
        try:
            # Valida a URL
            validate_url(url)
            
            # Define o diretório de saída
            if output_path is None:
                output_path = DOWNLOADS_DIR
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Verifica espaço em disco
            check_disk_space(str(output_path))
            
            # Cria a tarefa de download
            task = DownloadTask(
                url=url,
                output_path=output_path,
                format_info=format_info,
                callback=callback,
                preview_only=preview
            )
            
            # Adiciona à fila de download
            self.download_queue.put(task)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao iniciar download: {str(e)}")
            if callback:
                callback(False, str(e))
            return False

    def _process_download(self, task: DownloadTask, cancel_event: threading.Event) -> bool:
        """Processa o download de uma mídia."""
        try:
            # Prepara o comando yt-dlp
            cmd = ['yt-dlp']
            
            # Adiciona opções de formato
            format_str = f"-f bestvideo[ext={task.format_info['format']}]+bestaudio/best[ext={task.format_info['format']}]"
            if 'quality' in task.format_info:
                format_str += f"[height<={task.format_info['quality']}]"
            cmd.append(format_str)
            
            # Configura o arquivo de saída
            output_template = str(task.output_path / '%(title)s.%(ext)s')
            cmd.extend(['-o', output_template])
            
            # Adiciona outras opções
            if task.preview_only:
                cmd.extend(['--download-sections', f'*0:{PREVIEW_DURATION}'])
            
            # Adiciona a URL
            cmd.append(task.url)
            
            # Executa o download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitora o progresso
            while True:
                if cancel_event.is_set():
                    process.terminate()
                    raise DownloadError("Download cancelado pelo usuário")
                
                return_code = process.poll()
                if return_code is not None:
                    if return_code != 0:
                        raise DownloadError(f"Erro no download: {process.stderr.read()}")
                    break
                
                time.sleep(0.1)
            
            if task.callback:
                task.callback(True, "Download concluído com sucesso")
            return True
            
        except Exception as e:
            if task.callback:
                task.callback(False, str(e))
            raise DownloadError(str(e))

    def cancel_download(self, url: str) -> bool:
        """Cancela um download em andamento."""
        if url in self.cancel_events:
            self.cancel_events[url].set()
            return True
        return False

    def get_active_downloads(self) -> List[str]:
        """Retorna lista de downloads ativos."""
        return list(self.active_downloads.keys())

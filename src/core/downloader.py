"""Core downloader functionality."""
from pathlib import Path
import os
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, Callable, Dict
import yt_dlp
import time

from src.config.settings import (
    DOWNLOADS_DIR,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    VIDEO_QUALITIES,
    AUDIO_QUALITIES,
    ERROR_MESSAGES
)
from src.utils.utils import (
    validate_url,
    check_disk_space,
    ensure_dir,
    get_safe_filename,
    get_available_filename
)

@dataclass
class DownloadOptions:
    """Download configuration options."""
    format: str
    quality: str
    output_dir: str = DOWNLOADS_DIR
    playlist: bool = False
    convert_audio: bool = False

class DownloadError(Exception):
    """Custom exception for download-related errors."""
    pass

class MediaDownloader:
    """Handles downloading media from YouTube with progress tracking."""
    
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=8)
        self._active_downloads: Dict[str, Dict] = {}
        self._logger = logging.getLogger(__name__)
        self._current_download = None
        self._cancel_event = threading.Event()

    def download(self, url: str, options: DownloadOptions, 
                progress_callback: Optional[Callable] = None) -> str:
        """
        Start a download with the specified options.
        
        Args:
            url: YouTube URL to download from
            options: Download configuration options
            progress_callback: Optional callback for progress updates
            
        Returns:
            str: Download ID for tracking
            
        Raises:
            DownloadError: If download initialization fails
        """
        try:
            ydl_opts = self._build_ydl_options(options, progress_callback)
            download_id = str(len(self._active_downloads))
            
            future = self._executor.submit(
                self._download_media,
                url,
                ydl_opts,
                download_id
            )
            
            self._active_downloads[download_id] = {
                'future': future,
                'progress': 0,
                'status': 'downloading'
            }
            
            return download_id
            
        except Exception as e:
            self._logger.error(f"Failed to start download: {str(e)}")
            raise DownloadError(f"Failed to initialize download: {str(e)}")

    def _build_ydl_options(self, options: DownloadOptions, 
                          progress_callback: Optional[Callable]) -> dict:
        """Build options dictionary for yt-dlp."""
        output_template = str(Path(options.output_dir) / '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': self._get_format_string(options),
            'outtmpl': output_template,
            'progress_hooks': [
                lambda d: self._progress_hook(d, progress_callback)
            ],
            'quiet': True,
            'no_warnings': True
        }
        
        if options.convert_audio:
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': options.format.lower(),
                    'preferredquality': options.quality.replace('kbps', '')
                }]
            })
            
        return ydl_opts

    def _get_format_string(self, options: DownloadOptions) -> str:
        """Generate format string based on options."""
        if options.format in AUDIO_FORMATS.values():
            return 'bestaudio'
        
        quality_map = {
            '2160p (4K)': '2160',
            '1440p (2K)': '1440',
            '1080p': '1080',
            '720p': '720',
            '480p': '480',
            '360p': '360'
        }
        
        quality = quality_map.get(options.quality, '720')
        return f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'

    def _download_media(self, url: str, ydl_opts: dict, download_id: str) -> None:
        """Execute the actual download."""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self._active_downloads[download_id]['status'] = 'completed'
        except Exception as e:
            self._logger.error(f"Download failed: {str(e)}")
            self._active_downloads[download_id]['status'] = 'failed'
            self._active_downloads[download_id]['error'] = str(e)

    def _progress_hook(self, d: dict, callback: Optional[Callable]) -> None:
        """Handle download progress updates."""
        if d['status'] == 'downloading':
            progress = d.get('_percent_str', '0%').replace('%', '')
            try:
                progress = float(progress)
                if callback:
                    callback(progress)
            except ValueError:
                pass

    def get_download_status(self, download_id: str) -> Dict:
        """Get the current status of a download."""
        if download_id not in self._active_downloads:
            raise KeyError(f"Download ID {download_id} not found")
        
        return {
            'progress': self._active_downloads[download_id]['progress'],
            'status': self._active_downloads[download_id]['status'],
            'error': self._active_downloads[download_id].get('error')
        }

    def cancel_download(self, download_id: str) -> None:
        """Cancel an active download."""
        if download_id in self._active_downloads:
            self._active_downloads[download_id]['future'].cancel()
            self._active_downloads[download_id]['status'] = 'cancelled'

    def start_download(self, url: str):
        """Start the download process for the given URL."""
        self._cancel_event.clear()  # Clear the cancel event
        logging.info(f"Starting download for URL: {url}")  # Log for debugging
        self._current_download = self._executor.submit(self._download, url)
        logging.info(f"Download started for URL: {url}")  # Log for debugging
        logging.debug(f"Current download set: {self._current_download}")

    def _download(self, url: str):
        """Lógica de download real."""
        total_size = 100  # Simulando um tamanho total de download
        logging.info(f"Iniciando download para a URL: {url}")  # Log para depuração
        try:
            for i in range(total_size):  # Simulando progresso de download
                if self._cancel_event.is_set():
                    logging.info("Download cancelado.")
                    return
                time.sleep(0.1)  # Simular tempo necessário para o download
                logging.info(f"Baixado {i + 1}%")
                self.update_progress(i + 1, total_size)
        except Exception as e:
            logging.error(f"Falha no download: {e}")
        finally:
            self._current_download = None  # Resetar download atual após conclusão ou cancelamento
            logging.info("Download atual resetado.")

    def cancel(self):
        """Cancel the ongoing download completely and reset the downloader state."""
        if self._current_download:
            self._cancel_event.set()  # Set the cancel event
            logging.info("Cancel event set.")  # Log for debugging
            self._current_download.cancel()  # Cancel the current download task
            logging.info("Download request to cancel sent.")
            self._current_download = None  # Reset current download reference
        else:
            logging.warning("No current download to cancel.")  # Log if no download is active

        # Ensure that any ongoing processes are terminated
        logging.info("Downloader state reset. Ready for new download.")

    def update_progress(self, progress, total_size):
        # Este método deve ser implementado para atualizar o progresso na interface do usuário
        pass

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
    LOG_DIR, DOWNLOADS_DIR, CHUNK_SIZE, DOWNLOAD_TIMEOUT, MAX_DOWNLOAD_SIZE,
    PREVIEW_DURATION
)
from utils import (
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
    """YouTube media downloader with support for multiple formats and qualities.
    
    This class handles the downloading of media from YouTube URLs using yt-dlp.
    It supports various video and audio formats with different quality options.
    
    Attributes:
        VIDEO_FORMATS (dict): Supported video formats and their yt-dlp options
        AUDIO_FORMATS (dict): Supported audio formats and their yt-dlp options
        download_dir (Path): Directory where downloads will be saved
    
    Video Quality Levels:
        - High: Best available quality
        - Medium: 720p
        - Low: 480p
    
    Audio Quality Levels:
        - High: Best bitrate (e.g., 320kbps for MP3)
        - Medium: Medium bitrate (e.g., 192kbps for MP3)
        - Low: Lower bitrate (e.g., 128kbps for MP3)
    """
    
    VIDEO_FORMATS = {
        'mp4_high': {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'ext': 'mp4'},
        'mp4_medium': {'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best', 'ext': 'mp4'},
        'mp4_low': {'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best', 'ext': 'mp4'},
        'webm_high': {'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best', 'ext': 'webm'},
        'webm_medium': {'format': 'bestvideo[height<=720][ext=webm]+bestaudio[ext=webm]/best[height<=720][ext=webm]/best', 'ext': 'webm'},
        'webm_low': {'format': 'bestvideo[height<=480][ext=webm]+bestaudio[ext=webm]/best[height<=480][ext=webm]/best', 'ext': 'webm'},
        'mkv_high': {'format': 'bestvideo+bestaudio/best', 'ext': 'mkv'},
        'mkv_medium': {'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]', 'ext': 'mkv'},
        'mkv_low': {'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]', 'ext': 'mkv'}
    }
    
    AUDIO_FORMATS = {
        'mp3_high': {'format': 'bestaudio/best', 'ext': 'mp3', 'audio_quality': 0},
        'mp3_medium': {'format': 'bestaudio/best', 'ext': 'mp3', 'audio_quality': 5},
        'mp3_low': {'format': 'bestaudio/best', 'ext': 'mp3', 'audio_quality': 7},
        'aac_high': {'format': 'bestaudio/best', 'ext': 'm4a', 'audio_quality': 0},
        'aac_medium': {'format': 'bestaudio/best', 'ext': 'm4a', 'audio_quality': 5},
        'aac_low': {'format': 'bestaudio/best', 'ext': 'm4a', 'audio_quality': 7},
        'opus_high': {'format': 'bestaudio/best', 'ext': 'opus', 'audio_quality': 0},
        'opus_medium': {'format': 'bestaudio/best', 'ext': 'opus', 'audio_quality': 5},
        'opus_low': {'format': 'bestaudio/best', 'ext': 'opus', 'audio_quality': 7}
    }
    
    def __init__(self, download_dir=None):
        """Initialize the MediaDownloader.
        
        Args:
            download_dir (str or Path, optional): Directory to save downloads.
                Defaults to user's Downloads directory.
        """
        self.setup_logging()
        self.yt_dlp_path = "/home/piperun/my_yt_down/venv/bin/yt-dlp"
        self.download_dir = Path(download_dir) if download_dir else Path.home() / "Downloads"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def set_download_dir(self, path: Path):
        """Define o diretório de download."""
        self.download_dir = path
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def ensure_directories(self):
        """Garante que os diretórios necessários existam."""
        os.makedirs(LOG_DIR, exist_ok=True)

    def setup_logging(self):
        """Configura o sistema de logging."""
        os.makedirs(LOG_DIR, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(LOG_DIR, "downloader.log")),
                logging.StreamHandler()
            ]
        )

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

    def download_media(self, url, output_path, format_info, callback=None):
        """Download media from YouTube URL with specified format options.
        
        Args:
            url (str): YouTube URL to download from
            output_path (Path): Directory to save the downloaded file
            format_info (dict): Format and quality options
                Required keys:
                - format_type: "video" or "audio"
                - format_name: Format name from VIDEO_FORMATS or AUDIO_FORMATS
            callback (callable, optional): Function to call with download progress
                The function should accept a float parameter (progress percentage)
        
        Returns:
            bool: True if download was successful
        
        Raises:
            Exception: If download fails or format options are invalid
        """
        try:
            # Create task object
            task = DownloadTask(
                url=url,
                output_path=output_path,
                format_options=format_info,
                callback=callback
            )
            
            self.logger.info(f"Starting download: {task.url}")
            self.logger.debug(f"Format options: {task.format_options}")
            
            # Build command
            cmd = [
                self.yt_dlp_path,
                "--no-warnings",
                "--newline",
            ]
            
            # Add format options based on type
            if task.format_options.get("format_type") == "video":
                # Video format
                if task.format_options.get("format_name", "").startswith("mp4"):
                    cmd.extend([
                        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                        "--merge-output-format", "mp4"
                    ])
                elif task.format_options.get("format_name", "").startswith("webm"):
                    cmd.extend([
                        "-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
                        "--merge-output-format", "webm"
                    ])
                else:  # mkv or default
                    cmd.extend([
                        "-f", "bestvideo+bestaudio/best",
                        "--merge-output-format", "mkv"
                    ])
                
                # Add quality filter
                quality = task.format_options.get("format_name", "").split("_")[-1]
                if quality == "medium":
                    cmd.extend(["-f", "bestvideo[height<=720]+bestaudio/best[height<=720]"])
                elif quality == "low":
                    cmd.extend(["-f", "bestvideo[height<=480]+bestaudio/best[height<=480]"])
            
            else:
                # Audio format
                format_name = task.format_options.get("format_name", "mp3_high")
                format_parts = format_name.split("_")
                audio_format = format_parts[0]
                quality = format_parts[1] if len(format_parts) > 1 else "high"
                
                cmd.extend([
                    "-x",  # Extract audio
                    "--audio-format", audio_format
                ])
                
                # Set audio quality
                audio_quality = "0" if quality == "high" else "5" if quality == "medium" else "7"
                cmd.extend(["--audio-quality", audio_quality])
            
            # Set output template
            output_template = str(task.output_path / "%(title)s.%(ext)s")
            cmd.extend(["-o", output_template])
            
            # Add URL
            cmd.append(task.url)
            
            # Run download
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if "[download]" in line and "%" in line:
                    try:
                        progress = float(line.split("%")[0].split()[-1])
                        if task.callback:
                            task.callback(progress)
                    except (ValueError, IndexError):
                        pass
            
            # Check for errors
            if process.returncode != 0:
                error = process.stderr.read()
                raise Exception(f"Download failed: {error}")
            
            self.logger.info("Download completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Download error: {str(e)}")
            raise

    def preview_media(self, url: str, format_options: Dict) -> Optional[Path]:
        """Gera uma prévia da mídia."""
        try:
            validate_url(url)
            preview_dir = self.download_dir / "previews"
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
        # Not implemented

    def cleanup(self) -> None:
        """Limpa recursos do downloader."""
        # Not implemented

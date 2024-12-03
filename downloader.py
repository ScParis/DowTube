import os
import subprocess
import json
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from config import (
    FORMATS, MAX_RETRIES, RETRY_DELAY, MAX_CONCURRENT_DOWNLOADS,
    LOG_DIR, DOWNLOAD_DIR
)
from utils import validate_url, check_disk_space, sanitize_filename

class DownloadError(Exception):
    """Exceção customizada para erros de download."""
    pass

class MediaDownloader:
    def __init__(self):
        self.setup_logging()
        self.yt_dlp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "yt-dlp")
        self.ensure_directories()

    def setup_logging(self):
        """Configura o sistema de logging."""
        os.makedirs(LOG_DIR, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(LOG_DIR, "downloader.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def ensure_directories(self):
        """Garante que os diretórios necessários existam."""
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

    def get_media_info(self, url):
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
            return [json.loads(line) for line in result.stdout.splitlines()]
        except subprocess.CalledProcessError as e:
            raise DownloadError(f"Erro ao obter informações: {str(e)}")
        except json.JSONDecodeError as e:
            raise DownloadError(f"Erro ao processar informações: {str(e)}")

    def download_single(self, url, output_path, format_info, callback=None):
        """Download de um único vídeo/áudio com retry."""
        for attempt in range(MAX_RETRIES):
            try:
                cmd = [self.yt_dlp_path, "--output", output_path]
                
                if format_info["format"] == "mp3":
                    cmd.extend([
                        "-x",
                        "--audio-format", "mp3",
                        "--audio-quality", format_info["quality"]
                    ])
                else:
                    cmd.extend([
                        "-f", f"bestvideo[height<={format_info['quality']}]+bestaudio",
                        "--merge-output-format", "mp4"
                    ])
                
                cmd.append(url)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    if callback and "[download]" in line:
                        callback(line)

                process.communicate()
                if process.returncode == 0:
                    return True
                
                raise DownloadError(f"Download falhou com código {process.returncode}")
            
            except Exception as e:
                logging.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise DownloadError(f"Todas as tentativas falharam: {str(e)}")

    def download_playlist(self, url, output_dir, format_choice, quality, progress_callback=None):
        """Download de playlist com suporte a downloads paralelos."""
        try:
            validate_url(url)
            check_disk_space(output_dir)
            
            media_info = self.get_media_info(url)
            format_info = FORMATS[format_choice][quality]
            
            with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
                futures = []
                for item in media_info:
                    output_path = os.path.join(
                        output_dir,
                        f"{sanitize_filename(item.get('title', 'unknown'))}.%(ext)s"
                    )
                    future = executor.submit(
                        self.download_single,
                        item.get("webpage_url", url),
                        output_path,
                        format_info,
                        progress_callback
                    )
                    futures.append(future)
                
                return [future.result() for future in futures]
        
        except Exception as e:
            logging.exception("Erro durante o download")
            raise DownloadError(str(e))

    def get_available_formats(self):
        """Retorna os formatos disponíveis."""
        return FORMATS

    def cancel_downloads(self):
        """Cancela downloads em andamento."""
        # Implementação do cancelamento
        pass

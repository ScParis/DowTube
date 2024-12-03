import os

# Configurações de Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DOWNLOAD_DIR = os.path.expanduser("~/Downloads/YTDownloader")

# Configurações de Download
FORMATS = {
    "mp3": {
        "Alta Qualidade": {"format": "mp3", "quality": "320K"},
        "Média Qualidade": {"format": "mp3", "quality": "192K"},
        "Baixa Qualidade": {"format": "mp3", "quality": "128K"}
    },
    "mp4": {
        "1080p": {"format": "mp4", "quality": "1080"},
        "720p": {"format": "mp4", "quality": "720"},
        "480p": {"format": "mp4", "quality": "480"},
        "360p": {"format": "mp4", "quality": "360"}
    }
}

# Configurações de Retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos

# Configurações de Validação
MIN_DISK_SPACE = 1024  # MB
VALID_URL_REGEX = r"^https?://(?:www\.)?youtube\.com/watch\?v=.+|^https?://(?:www\.)?youtube\.com/playlist\?list=.+"

# Configurações de Download Paralelo
MAX_CONCURRENT_DOWNLOADS = 2

# Configurações de Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOG_DIR, "downloader.log")

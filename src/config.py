import os
from pathlib import Path

# Configurações de Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
DOWNLOADS_DIR = Path.home() / "Downloads" / "YTDownloader"
FAVORITES_DIR = BASE_DIR / "favorites"

# Configurações de Download
FORMATS = {
    "audio": {
        "mp3": {
            "Alta Qualidade": {"format": "mp3", "quality": "320K"},
            "Média Qualidade": {"format": "mp3", "quality": "192K"},
            "Baixa Qualidade": {"format": "mp3", "quality": "128K"}
        },
        "wav": {"Sem Compressão": {"format": "wav"}},
        "ogg": {"Padrão": {"format": "ogg"}},
        "m4a": {"Padrão": {"format": "m4a"}}
    },
    "video": {
        "mp4": {
            "1080p": {"format": "mp4", "quality": "1080"},
            "720p": {"format": "mp4", "quality": "720"},
            "480p": {"format": "mp4", "quality": "480"},
            "360p": {"format": "mp4", "quality": "360"}
        },
        "webm": {
            "1080p": {"format": "webm", "quality": "1080"},
            "720p": {"format": "webm", "quality": "720"}
        }
    }
}

# Configurações de Download
CHUNK_SIZE = 8192  # bytes
DOWNLOAD_TIMEOUT = 30  # segundos
MAX_DOWNLOAD_SIZE = 2048  # MB
PREVIEW_DURATION = 30  # segundos

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

# Configurações de Tema
THEMES = {
    "light": {
        "bg_color": "#ffffff",
        "fg_color": "#000000",
        "accent_color": "#007bff",
        "error_color": "#dc3545",
        "success_color": "#28a745"
    },
    "dark": {
        "bg_color": "#1a1a1a",
        "fg_color": "#ffffff",
        "accent_color": "#0d6efd",
        "error_color": "#dc3545",
        "success_color": "#28a745"
    }
}

# Configurações de Download
DOWNLOAD_SETTINGS = {
    "max_retries": MAX_RETRIES,
    "retry_delay": RETRY_DELAY,
    "chunk_size": CHUNK_SIZE,
    "timeout": DOWNLOAD_TIMEOUT,
    "max_size": MAX_DOWNLOAD_SIZE,
    "preview_duration": PREVIEW_DURATION
}

# Configurações de Playlist
PLAYLIST_SETTINGS = {
    "download_all": False,
    "reverse_order": False,
    "max_items": 50,
    "skip_existing": True
}

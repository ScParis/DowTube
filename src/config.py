import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"  # Diretório para logs
TEMP_DOWNLOADS_DIR = BASE_DIR / "temp_downloads"  # Diretório temporário para downloads
DOWNLOADS_DIR = BASE_DIR / "downloads"  # Diretório para downloads finais
FAVORITES_DIR = BASE_DIR / "favorites"

# Configurações de download
MAX_CONCURRENT_DOWNLOADS = 2
DOWNLOAD_TIMEOUT = 30  # segundos
MAX_DOWNLOAD_SIZE = 2048  # MB
CHUNK_SIZE = 8192  # bytes
PREVIEW_DURATION = 30  # segundos

# Configurações de rate limit
RATE_LIMIT_REQUESTS = 30  # Número máximo de requisições
RATE_LIMIT_PERIOD = 60   # Período em segundos
RATE_LIMIT_BURST = 10    # Tamanho máximo do burst
RATE_LIMIT_COOLDOWN = 5  # Tempo de espera entre tentativas (segundos)

# Configurações de retry
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos

# Validação
MIN_DISK_SPACE = 1024 * 1024 * 1024  # 1 GB em bytes
VALID_URL_REGEX = r'^(https?://)?(www\.)?(music\.youtube\.com|youtube\.com|youtu\.be)/.+$'

# Formatos de download disponíveis
FORMATS = {
    "audio": {
        "mp3": {
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }]
        },
        "wav": {
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0"
            }]
        },
        "ogg": {
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "vorbis",
                "preferredquality": "192"
            }]
        },
        "m4a": {
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "256"
            }]
        }
    },
    "video": {
        "mp4": {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4"
        },
        "webm": {
            "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
            "merge_output_format": "webm"
        }
    }
}

# Qualidades de áudio disponíveis (em kbps)
AUDIO_QUALITIES = ["64", "128", "192", "256", "320"]

# Qualidades de vídeo disponíveis
VIDEO_QUALITIES = {
    "144p": "144",
    "240p": "240",
    "360p": "360",
    "480p": "480",
    "720p": "720",
    "1080p": "1080",
    "1440p": "1440",
    "2160p": "2160"
}

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

import os
from pathlib import Path

# Diretórios Base
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DOWNLOADS_DIR = BASE_DIR / "downloads"
LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"

# Criar diretórios necessários
for directory in [DOWNLOADS_DIR, LOG_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# Configurações de Download
CHUNK_SIZE = 8192  # Tamanho do buffer para download
DOWNLOAD_TIMEOUT = 30  # Timeout para downloads em segundos
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos
MAX_CONCURRENT_DOWNLOADS = 2

# Configurações de Cache
VIDEO_CACHE_TIME = 3600  # 1 hora
MAX_CACHE_SIZE = 100 * 1024 * 1024  # 100MB

# Formatos de Download
FORMATS = {
    "mp3": {
        "Alta Qualidade": {"format": "mp3", "quality": "320K", "description": "Áudio em alta qualidade (320kbps)"},
        "Média Qualidade": {"format": "mp3", "quality": "192K", "description": "Áudio em qualidade média (192kbps)"},
        "Baixa Qualidade": {"format": "mp3", "quality": "128K", "description": "Áudio em qualidade básica (128kbps)"}
    },
    "mp4": {
        "1080p": {"format": "mp4", "quality": "1080", "description": "Vídeo em Full HD"},
        "720p": {"format": "mp4", "quality": "720", "description": "Vídeo em HD"},
        "480p": {"format": "mp4", "quality": "480", "description": "Vídeo em qualidade padrão"},
        "360p": {"format": "mp4", "quality": "360", "description": "Vídeo em baixa qualidade"}
    }
}

# Formatos Padrão
DEFAULT_FORMATS = {
    "mp3": "Alta Qualidade",
    "mp4": "1080p"
}

# Configurações de Interface
RECENT_DOWNLOADS_COUNT = 10
THEME_SETTINGS = {
    "dark": {
        "background": "#2B2B2B",
        "foreground": "#FFFFFF",
        "accent": "#007AFF",
        "error": "#FF3B30",
        "success": "#34C759"
    },
    "light": {
        "background": "#F5F5F5",
        "foreground": "#000000",
        "accent": "#007AFF",
        "error": "#FF3B30",
        "success": "#34C759"
    }
}

# Configurações de Validação
MIN_DISK_SPACE = 1024  # MB
VALID_URL_REGEX = r"^https?://(?:www\.)?youtube\.com/watch\?v=.+|^https?://(?:www\.)?youtube\.com/playlist\?list=.+"
SUPPORTED_PLATFORMS = ["youtube", "youtube_music"]

# Configurações de Recursos
MAX_FAVORITES = 100
MAX_SCHEDULED_DOWNLOADS = 50
PREVIEW_DURATION = 30  # segundos

# Configurações de Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOG_DIR / "downloader.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Configurações de Segurança
MAX_DOWNLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
ALLOWED_DOMAINS = ["youtube.com", "youtu.be", "music.youtube.com"]
API_RATE_LIMIT = 100  # requisições por minuto

# Configurações de Performance
MEMORY_LIMIT = 512 * 1024 * 1024  # 512MB
CPU_LIMIT = 80  # porcentagem máxima de CPU

import os
from pathlib import Path
from typing import Dict, List

# Diretórios Base
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DOWNLOADS_DIR = BASE_DIR / "downloads"
LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
FAVORITES_DIR = BASE_DIR / "favorites"

# Criar diretórios necessários
for directory in [DOWNLOADS_DIR, LOG_DIR, CACHE_DIR, FAVORITES_DIR]:
    directory.mkdir(exist_ok=True)

# Configurações de Download
CHUNK_SIZE = 8192  # Tamanho do buffer para download
DOWNLOAD_TIMEOUT = 30  # Timeout para downloads em segundos
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos
MAX_CONCURRENT_DOWNLOADS = os.cpu_count() or 2  # Usa número de CPUs ou 2 como padrão
RATE_LIMIT = 1024 * 1024 * 10  # 10MB/s por download

# Configurações de Cache
VIDEO_CACHE_TIME = 3600  # 1 hora
MAX_CACHE_SIZE = 500 * 1024 * 1024  # 500MB

# Configurações de Interface
THEMES = {
    "dark": {
        "bg_color": "#2b2b2b",
        "fg_color": "#ffffff",
        "accent_color": "#007acc"
    },
    "light": {
        "bg_color": "#ffffff",
        "fg_color": "#2b2b2b",
        "accent_color": "#007acc"
    },
    "system": "system"  # Usa o tema do sistema
}

# Formatos de Download
FORMATS: Dict[str, Dict] = {
    "audio": {
        "mp3": {
            "Alta Qualidade": {"format": "mp3", "quality": "320K", "description": "Áudio em alta qualidade (320kbps)"},
            "Média Qualidade": {"format": "mp3", "quality": "192K", "description": "Áudio em qualidade média (192kbps)"},
            "Baixa Qualidade": {"format": "mp3", "quality": "128K", "description": "Áudio em qualidade básica (128kbps)"}
        },
        "wav": {
            "PCM": {"format": "wav", "quality": "pcm", "description": "Áudio sem compressão"},
        },
        "ogg": {
            "Alta Qualidade": {"format": "ogg", "quality": "10", "description": "Áudio Ogg Vorbis alta qualidade"},
            "Média Qualidade": {"format": "ogg", "quality": "6", "description": "Áudio Ogg Vorbis qualidade média"},
        },
        "m4a": {
            "Alta Qualidade": {"format": "m4a", "quality": "192K", "description": "Áudio AAC alta qualidade"},
            "Média Qualidade": {"format": "m4a", "quality": "128K", "description": "Áudio AAC qualidade média"},
        }
    },
    "video": {
        "mp4": {
            "4K": {"format": "mp4", "quality": "2160", "description": "Vídeo 4K (3840x2160)"},
            "2K": {"format": "mp4", "quality": "1440", "description": "Vídeo 2K (2560x1440)"},
            "1080p": {"format": "mp4", "quality": "1080", "description": "Vídeo Full HD (1920x1080)"},
            "720p": {"format": "mp4", "quality": "720", "description": "Vídeo HD (1280x720)"},
            "480p": {"format": "mp4", "quality": "480", "description": "Vídeo SD (854x480)"},
            "360p": {"format": "mp4", "quality": "360", "description": "Vídeo LD (640x360)"}
        },
        "webm": {
            "1080p": {"format": "webm", "quality": "1080", "description": "WebM Full HD"},
            "720p": {"format": "webm", "quality": "720", "description": "WebM HD"},
        }
    }
}

# Configurações de Download
DOWNLOAD_SETTINGS = {
    "verify_integrity": True,  # Verifica integridade do arquivo após download
    "auto_retry": True,  # Tenta novamente automaticamente em caso de falha
    "rate_limit_enabled": True,  # Ativa limite de velocidade
    "notify_complete": True,  # Notificação ao completar download
    "auto_organize": True,  # Organiza downloads por tipo/data
    "preview_enabled": True,  # Habilita preview antes do download
    "scheduler_enabled": True,  # Habilita agendamento de downloads
}

# Configurações de Playlist
PLAYLIST_SETTINGS = {
    "download_all": False,  # Download automático de toda playlist
    "max_items": 100,  # Número máximo de itens por playlist
    "reverse_order": False,  # Ordem reversa de download
    "skip_existing": True,  # Pula arquivos já baixados
}

# Configurações de Segurança
SECURITY_SETTINGS = {
    "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
    "allowed_domains": ["youtube.com", "youtu.be", "youtube-nocookie.com"],
    "verify_ssl": True,
    "max_daily_downloads": 100,
}

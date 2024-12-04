import os
import re
import logging
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import requests

from .config import (
    VALID_URL_REGEX, MIN_DISK_SPACE, LOG_FORMAT,
    LOG_FILE, LOG_DIR, SECURITY_SETTINGS,
    DOWNLOAD_SETTINGS, CACHE_DIR
)

class ValidationError(Exception):
    """Exceção customizada para erros de validação."""
    pass

def validate_url(url: str) -> bool:
    """Valida a URL do YouTube."""
    if not url:
        raise ValidationError("URL não pode estar vazia")
    if not re.match(VALID_URL_REGEX, url):
        raise ValidationError("URL inválida. Deve ser uma URL válida do YouTube")
    try:
        parsed = urlparse(url)
        if parsed.netloc not in SECURITY_SETTINGS["allowed_domains"]:
            raise ValidationError("Domínio não permitido")
    except Exception as e:
        raise ValidationError(f"URL inválida: {str(e)}")
    return True

def check_disk_space(path: str) -> bool:
    """Verifica se há espaço em disco suficiente."""
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (1024 * 1024)
        if free_mb < MIN_DISK_SPACE:
            raise ValidationError(f"Espaço em disco insuficiente. Necessário: {MIN_DISK_SPACE}MB, Disponível: {free_mb}MB")
        return True
    except Exception as e:
        raise ValidationError(f"Erro ao verificar espaço em disco: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos do nome do arquivo."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def format_size(size_bytes: float) -> str:
    """Formata o tamanho em bytes para formato legível."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def format_duration(seconds: int) -> str:
    """Formata duração em segundos para formato legível."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    return f"{int(seconds)}s"

def setup_logger(name: str) -> logging.Logger:
    """Configura e retorna um logger."""
    # Cria o diretório de logs se não existir
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    return logger

def cache_manager(func):
    """Decorator para gerenciar cache de downloads."""
    cache: Dict[str, Any] = {}
    
    def wrapper(*args, **kwargs):
        cache_key = str(args) + str(kwargs)
        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)
        return cache[cache_key]
    
    return wrapper

def download_history(func):
    """Decorator para registrar histórico de downloads."""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        # Registra o download no histórico
        history_entry = {
            "url": args[1] if len(args) > 1 else kwargs.get("url"),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": str(end_time - start_time),
            "success": True if result else False
        }
        
        # TODO: Implementar persistência do histórico
        
        return result
    
    return wrapper

class CacheManager:
    """Gerencia o cache de informações de vídeo."""
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "video_cache.json"
        self.cache: Dict[str, Any] = self.load_cache()

    def load_cache(self) -> Dict[str, Any]:
        """Carrega o cache do disco."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_cache(self):
        """Salva o cache no disco."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """Obtém informações do cache."""
        key = self._generate_key(url)
        if key in self.cache:
            data = self.cache[key]
            # Verifica se o cache ainda é válido
            if datetime.now().timestamp() - data['timestamp'] < 3600:
                return data['info']
            else:
                del self.cache[key]
                self.save_cache()
        return None

    def set(self, url: str, info: Dict[str, Any]):
        """Armazena informações no cache."""
        key = self._generate_key(url)
        self.cache[key] = {
            'info': info,
            'timestamp': datetime.now().timestamp()
        }
        self.save_cache()
        self._cleanup_cache()

    def _generate_key(self, url: str) -> str:
        """Gera uma chave única para a URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _cleanup_cache(self):
        """Remove entradas antigas do cache."""
        now = datetime.now().timestamp()
        self.cache = {
            k: v for k, v in self.cache.items()
            if now - v['timestamp'] < 3600
        }
        self.save_cache()

class DownloadHistory:
    """Gerencia o histórico de downloads."""
    
    def __init__(self):
        self.history_file = LOG_DIR / "download_history.json"
        self.history: Dict[str, Any] = self.load_history()

    def load_history(self) -> Dict[str, Any]:
        """Carrega o histórico do disco."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'downloads': []}

    def save_history(self):
        """Salva o histórico no disco."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def add_download(self, url: str, format_info: Dict[str, Any], 
                    output_path: Path, status: str = "success"):
        """Adiciona um download ao histórico."""
        download_info = {
            'url': url,
            'format': format_info,
            'output_path': str(output_path),
            'timestamp': datetime.now().isoformat(),
            'status': status
        }
        self.history['downloads'].insert(0, download_info)
        
        # Limita o tamanho do histórico
        max_history = 1000
        if len(self.history['downloads']) > max_history:
            self.history['downloads'] = self.history['downloads'][:max_history]
        
        self.save_history()

    def get_downloads(self, limit: Optional[int] = None) -> list:
        """Retorna os downloads mais recentes."""
        downloads = self.history['downloads']
        return downloads[:limit] if limit else downloads

    def clear_history(self):
        """Limpa o histórico de downloads."""
        self.history['downloads'] = []
        self.save_history()

def verify_file_integrity(file_path: Path) -> bool:
    """Verifica a integridade de um arquivo baixado."""
    if not DOWNLOAD_SETTINGS["verify_integrity"]:
        return True
    
    try:
        # Verifica se o arquivo existe e não está vazio
        if not file_path.exists() or file_path.stat().st_size == 0:
            return False

        # Verifica se o arquivo pode ser aberto
        with open(file_path, 'rb') as f:
            # Lê os primeiros bytes para verificar se não estão corrompidos
            header = f.read(1024)
            if not header:
                return False

        return True
    except Exception:
        return False

# Instâncias globais
cache_manager = CacheManager()
download_history = DownloadHistory()
logger = setup_logger('utils')

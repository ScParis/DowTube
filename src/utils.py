import os
import re
import json
import logging
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import requests

from src.config import (
    LOG_DIR, CACHE_DIR, SECURITY_SETTINGS,
    DOWNLOAD_SETTINGS
)

class ValidationError(Exception):
    """Exceção para erros de validação."""
    pass

def setup_logger(name: str) -> logging.Logger:
    """Configura e retorna um logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Handler de arquivo
    log_file = LOG_DIR / f"{name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Handler de console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def validate_url(url: str) -> bool:
    """Valida uma URL do YouTube."""
    try:
        parsed = urlparse(url)
        if parsed.netloc not in SECURITY_SETTINGS["allowed_domains"]:
            raise ValidationError("Domínio não permitido")
        
        # Verifica se é uma URL válida do YouTube
        patterns = [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://youtu\.be/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+'
        ]
        
        return any(re.match(pattern, url) for pattern in patterns)
    
    except Exception as e:
        raise ValidationError(f"URL inválida: {str(e)}")

def check_disk_space(path: Path, required_bytes: int) -> bool:
    """Verifica se há espaço em disco suficiente."""
    try:
        total, used, free = shutil.disk_usage(path)
        return free > required_bytes
    except Exception as e:
        raise ValidationError(f"Erro ao verificar espaço em disco: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """Sanitiza o nome do arquivo para ser seguro em qualquer sistema."""
    # Remove caracteres inválidos
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Remove espaços extras e pontos no final
    filename = re.sub(r'\s+', ' ', filename).strip().rstrip('.')
    
    # Limita o tamanho do nome
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    
    return filename

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

import os
import shutil
import re
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
from config import (
    VALID_URL_REGEX, MIN_DISK_SPACE, CACHE_DIR, VIDEO_CACHE_TIME,
    MAX_CACHE_SIZE, ALLOWED_DOMAINS
)

class ValidationError(Exception):
    """Exceção para erros de validação."""
    pass

class CacheManager:
    """Gerenciador de cache para informações de vídeos."""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self._cleanup_old_cache()

    def _get_cache_path(self, url: str) -> Path:
        """Gera o caminho do arquivo de cache para uma URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"

    def get(self, url: str) -> Optional[Dict]:
        """Recupera informações em cache para uma URL."""
        cache_path = self._get_cache_path(url)
        if not cache_path.exists():
            return None

        with cache_path.open('r') as f:
            data = json.load(f)
            if time.time() - data['timestamp'] > VIDEO_CACHE_TIME:
                cache_path.unlink()
                return None
            return data['info']

    def set(self, url: str, info: Dict):
        """Armazena informações em cache para uma URL."""
        cache_path = self._get_cache_path(url)
        data = {
            'timestamp': time.time(),
            'info': info
        }
        with cache_path.open('w') as f:
            json.dump(data, f)

    def _cleanup_old_cache(self):
        """Remove arquivos de cache antigos."""
        current_time = time.time()
        total_size = 0
        files = []

        for cache_file in self.cache_dir.glob('*.json'):
            stats = cache_file.stat()
            age = current_time - stats.st_mtime
            if age > VIDEO_CACHE_TIME:
                cache_file.unlink()
            else:
                total_size += stats.st_size
                files.append((cache_file, stats.st_mtime))

        if total_size > MAX_CACHE_SIZE:
            files.sort(key=lambda x: x[1])  # Ordena por data de modificação
            for file, _ in files:
                file.unlink()
                total_size -= file.stat().st_size
                if total_size <= MAX_CACHE_SIZE:
                    break

class DownloadHistory:
    """Gerenciador de histórico de downloads."""
    
    def __init__(self):
        self.history_file = CACHE_DIR / "download_history.json"
        self.history: List[Dict] = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Carrega o histórico de downloads."""
        if self.history_file.exists():
            with self.history_file.open('r') as f:
                return json.load(f)
        return []

    def add_entry(self, url: str, format: str, quality: str, status: str):
        """Adiciona uma entrada ao histórico."""
        entry = {
            'url': url,
            'format': format,
            'quality': quality,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        self.history.insert(0, entry)
        self.history = self.history[:100]  # Mantém apenas os últimos 100 downloads
        self._save_history()

    def _save_history(self):
        """Salva o histórico em arquivo."""
        with self.history_file.open('w') as f:
            json.dump(self.history, f)

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Retorna os downloads mais recentes."""
        return self.history[:limit]

def validate_url(url: str) -> bool:
    """Valida a URL do YouTube."""
    if not url:
        raise ValidationError("URL não pode estar vazia")
    
    if not re.match(VALID_URL_REGEX, url):
        raise ValidationError("URL inválida. Deve ser uma URL válida do YouTube")
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '')
    
    if domain not in ALLOWED_DOMAINS:
        raise ValidationError(f"Domínio não permitido. Use apenas: {', '.join(ALLOWED_DOMAINS)}")
    
    return True

def check_disk_space(path: Union[str, Path]) -> bool:
    """Verifica se há espaço em disco suficiente."""
    try:
        total, used, free = shutil.disk_usage(str(path))
        free_mb = free // (1024 * 1024)
        if free_mb < MIN_DISK_SPACE:
            raise ValidationError(
                f"Espaço em disco insuficiente. "
                f"Necessário: {MIN_DISK_SPACE}MB, Disponível: {free_mb}MB"
            )
        return True
    except Exception as e:
        raise ValidationError(f"Erro ao verificar espaço em disco: {str(e)}")

def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos do nome do arquivo."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()[:255]  # Limita o tamanho do nome do arquivo

def format_size(size_bytes: int) -> str:
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
    """Configura um logger personalizado."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler de arquivo
    file_handler = logging.FileHandler(CACHE_DIR / f"{name}.log")
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    return logger

# Inicializa gerenciadores globais
cache_manager = CacheManager()
download_history = DownloadHistory()

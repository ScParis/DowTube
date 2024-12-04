import os
import shutil
import re
from .config import VALID_URL_REGEX, MIN_DISK_SPACE

class ValidationError(Exception):
    """Exceção customizada para erros de validação."""
    pass

def validate_url(url):
    """Valida a URL do YouTube."""
    if not url:
        raise ValidationError("URL não pode estar vazia")
    if not re.match(VALID_URL_REGEX, url):
        raise ValidationError("URL inválida. Deve ser uma URL válida do YouTube")
    return True

def check_disk_space(path):
    """Verifica se há espaço em disco suficiente."""
    try:
        total, used, free = shutil.disk_usage(path)
        free_mb = free // (1024 * 1024)
        if free_mb < MIN_DISK_SPACE:
            raise ValueError(f"Espaço em disco insuficiente. Necessário: {MIN_DISK_SPACE}MB, Disponível: {free_mb}MB")
        return True
    except Exception as e:
        raise ValueError(f"Erro ao verificar espaço em disco: {str(e)}")

def sanitize_filename(filename):
    """Remove caracteres inválidos do nome do arquivo."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def format_size(size_bytes):
    """Formata o tamanho em bytes para formato legível."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def format_duration(seconds):
    """Formata duração em segundos para formato legível."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    return f"{int(seconds)}s"

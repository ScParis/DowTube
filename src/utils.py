import os
import shutil
import re
from pathlib import Path
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
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    
    free_space = shutil.disk_usage(path).free
    if free_space < MIN_DISK_SPACE:
        raise ValidationError(
            f"Espaço em disco insuficiente. Necessário: {MIN_DISK_SPACE} bytes, "
            f"Disponível: {free_space} bytes"
        )
    return True

def sanitize_filename(filename):
    """Sanitiza o nome do arquivo para ser seguro em qualquer sistema de arquivos."""
    # Remove caracteres inválidos
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove espaços em branco no início e fim
    filename = filename.strip()
    
    # Substitui espaços por underscore
    filename = filename.replace(' ', '_')
    
    # Limita o tamanho do nome do arquivo
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def format_size(size_bytes):
    """Formata o tamanho em bytes para uma string legível."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def format_duration(seconds):
    """Formata a duração em segundos para uma string legível."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    return f"{int(minutes):02d}:{int(seconds):02d}"

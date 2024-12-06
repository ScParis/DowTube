"""Utility functions for the YouTube Downloader application."""
import os
import re
import shutil
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, parse_qs

from src.config.settings import VALID_URL_REGEX, MIN_DISK_SPACE

def validate_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    return bool(VALID_URL_REGEX.match(url))

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        str: Video ID if found, None otherwise
    """
    if not validate_url(url):
        return None
        
    parsed = urlparse(url)
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
    elif parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    return None

def check_disk_space(path: str, required_space: int = MIN_DISK_SPACE) -> bool:
    """Check if there's enough disk space available.
    
    Args:
        path: Path to check disk space for
        required_space: Required space in bytes
        
    Returns:
        bool: True if enough space available, False otherwise
    """
    try:
        total, used, free = shutil.disk_usage(path)
        return free >= required_space
    except Exception as e:
        logging.error(f"Failed to check disk space: {e}")
        return False

def ensure_dir(path: str) -> bool:
    """Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        bool: True if directory exists or was created, False on error
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False

def get_safe_filename(filename: str) -> str:
    """Convert filename to safe version by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove or replace other problematic characters
    safe_name = safe_name.replace('..', '.')
    safe_name = safe_name.strip('. ')  # Remove dots and spaces from start/end
    
    # Ensure the filename isn't empty after cleaning
    if not safe_name:
        safe_name = 'unnamed_file'
        
    return safe_name

def get_available_filename(directory: str, filename: str) -> str:
    """Get an available filename by adding a number if file exists.
    
    Args:
        directory: Target directory
        filename: Desired filename
        
    Returns:
        str: Available filename
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
        
    return new_filename

def format_size(size_bytes: int) -> str:
    """Format file size from bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def format_time(seconds: int) -> str:
    """Format time in seconds to HH:MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"

def read_logs(max_lines: Optional[int] = None) -> str:
    """Read the contents of the log files.
    
    Args:
        max_lines: Maximum number of lines to read (from newest). If None, read all lines.
    
    Returns:
        str: The contents of the log files.
    """
    try:
        logs_dir = os.path.expanduser("~/.my-yt-down/logs")
        if not os.path.exists(logs_dir):
            return "No logs found."
            
        # Get list of log files sorted by modification time (newest first)
        log_files = sorted(
            Path(logs_dir).glob("*.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not log_files:
            return "No logs found."
            
        # Read the contents of all log files
        all_logs = []
        for log_file in log_files:
            with open(log_file, 'r') as f:
                logs = f.readlines()
                if max_lines:
                    logs = logs[-max_lines:]
                all_logs.extend(logs)
        
        # If max_lines specified, only return the last max_lines
        if max_lines:
            all_logs = all_logs[-max_lines:]
            
        return "".join(all_logs)
        
    except Exception as e:
        logging.error(f"Failed to read logs: {e}")
        return f"Error reading logs: {e}"

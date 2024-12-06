"""Application settings and constants."""
import os
import re
from pathlib import Path

# Directories
SRC_DIR = Path(__file__).parent.parent
BASE_DIR = SRC_DIR.parent
DOWNLOADS_DIR = str(Path.home() / "Downloads" / "YouTube")
LOGS_DIR = str(Path.home() / ".my-yt-down" / "logs")

# System requirements
MIN_DISK_SPACE = 1024 * 1024 * 1024  # 1GB in bytes

# Validation
VALID_URL_REGEX = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]{11}$'
)

# Download settings
MAX_CONCURRENT_DOWNLOADS = 3
DEFAULT_THEME = "blue"
DEFAULT_APPEARANCE = "System"

# Media formats
VIDEO_FORMATS = {
    'MP4': 'mp4',
    'WebM': 'webm',
    'MKV': 'mkv'
}

AUDIO_FORMATS = {
    'MP3': 'mp3',
    'AAC': 'aac',
    'Opus': 'opus',
    'WAV': 'wav'
}

VIDEO_QUALITIES = [
    '2160p',  # 4K
    '1440p',  # 2K
    '1080p',  # Full HD
    '720p',   # HD
    '480p',   # SD
    '360p',
    '240p',
    '144p'
]

AUDIO_QUALITIES = [
    'Best',
    'High',
    'Medium',
    'Low'
]

# Error messages
ERROR_MESSAGES = {
    'invalid_url': 'Invalid YouTube URL. Please enter a valid URL.',
    'download_failed': 'Failed to download video. Please try again.',
    'disk_space': 'Not enough disk space. Please free up some space and try again.',
    'network_error': 'Network error. Please check your internet connection.',
    'file_error': 'Error saving file. Please check write permissions.',
    'unknown_error': 'An unknown error occurred. Please try again.',
    'no_permission': "No permission to write to the selected directory.",
    'network_error': "Network error. Please check your internet connection.",
}

# GUI settings
WINDOW_SIZE = "800x600"
MIN_WINDOW_SIZE = (700, 800)
PADDING = {
    'small': 5,
    'medium': 10,
    'large': 20
}

# UI Settings
COLORS = {
    'bg_dark': '#1c1c1c',
    'bg_light': '#2d2d2d',
    'primary': '#2962ff',
    'primary_hover': '#1e88e5',
    'text': '#ffffff',
    'error': '#f44336',
    'success': '#4caf50'
}

# Window Settings
WINDOW_SETTINGS = {
    'width': 1200,
    'height': 800,
    'min_width': 1000,
    'min_height': 600
}

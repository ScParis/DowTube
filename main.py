"""Main entry point for the YouTube Downloader application."""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root directory to Python path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Configure logging
from src.config.settings import LOGS_DIR
os.makedirs(LOGS_DIR, exist_ok=True)
log_file = os.path.join(LOGS_DIR, f"youtube_downloader_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

from src.gui import DownloaderGUI

if __name__ == "__main__":
    app = DownloaderGUI()
    app.mainloop()

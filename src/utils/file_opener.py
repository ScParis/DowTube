"""File and directory utilities."""
import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

def open_logs_directory() -> bool:
    """Open the logs directory in the system's file explorer."""
    try:
        logs_dir = os.path.expanduser("~/.my-yt-down/logs")
        if os.path.exists(logs_dir):
            subprocess.run(['xdg-open', logs_dir])
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to open logs directory: {e}")
        return False

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

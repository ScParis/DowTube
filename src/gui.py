import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import sys
import logging
import json
from src.utils.file_opener import open_logs_directory

from .downloader import MediaDownloader, DownloadError
from .config import (
    FORMATS, DOWNLOADS_DIR, AUDIO_QUALITIES,
    VIDEO_QUALITIES, MAX_CONCURRENT_DOWNLOADS, BASE_DIR
)

class DownloaderGUI(ctk.CTk):
    """YouTube Downloader GUI application.
    
    A modern, user-friendly interface for downloading YouTube videos and audio
    with support for multiple formats and quality options.
    
    Features:
        - Video downloads (MP4, WebM, MKV)
        - Audio downloads (MP3, AAC, Opus)
        - Multiple quality options
        - Custom save location
        - Download progress tracking
        - Error handling
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        super().__init__()
        
        # Basic setup
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("YouTube Downloader")
        self.geometry("800x600")
        self.minsize(700, 800)
        
        # Initialize
        self.config = self.load_config()
        self.download_dir = self.config.get('download_dir', DOWNLOADS_DIR)
        self.downloader = MediaDownloader(download_dir=self.download_dir)
        self.active_downloads = {}
        
        # Create menu
        self.create_menu()
        
        # Setup interface
        self.create_widgets()
    
    def create_menu(self):
        """Cria a barra de menu."""
        # Frame para o menu
        menu_frame = ctk.CTkFrame(self)
        menu_frame.pack(fill="x", padx=5, pady=5)
        
        # Botão de Ajuda
        help_button = ctk.CTkButton(
            menu_frame,
            text="?",
            width=30,
            command=self.show_help
        )
        help_button.pack(side="right", padx=5)
        
        # Botão de Logs
        logs_button = ctk.CTkButton(
            menu_frame,
            text="📋 Logs",
            width=80,
            command=self.open_logs
        )
        logs_button.pack(side="right", padx=5)
    
    def open_logs(self):
        """Abre o diretório de logs."""
        if not open_logs_directory():
            # Se falhar ao abrir, mostrar mensagem de erro
            self.show_error("Não foi possível abrir o diretório de logs.\nVerifique o console para mais detalhes.")
    
    def show_help(self):
        """Mostra a janela de ajuda."""
        help_window = ctk.CTkToplevel(self)
        help_window.title("Ajuda")
        help_window.geometry("600x400")
        
        # Texto de ajuda
        help_text = ctk.CTkTextbox(help_window)
        help_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_content = """
        YouTube Downloader - Ajuda
        
        1. Como usar:
           - Cole a URL do vídeo do YouTube
           - Escolha o formato desejado
           - Selecione a qualidade
           - Clique em Download
        
        2. Formatos suportados:
           - Vídeo: MP4, WebM, MKV
           - Áudio: MP3, AAC, Opus
        
        3. Logs de erro:
           - Clique no botão "📋 Logs" para acessar os logs
           - Os logs são salvos em ~/.my-yt-down/logs/
           - Cada arquivo de log é nomeado com a data
        
        4. Em caso de problemas:
           - Verifique os logs de erro
           - Certifique-se de ter uma conexão estável
           - Verifique se o vídeo está disponível
           - Verifique as permissões de escrita
        """
        
        help_text.insert("1.0", help_content)
        help_text.configure(state="disabled")
    
    def show_error(self, message):
        """Mostra uma mensagem de erro."""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Erro")
        error_window.geometry("400x200")
        
        # Mensagem de erro
        error_label = ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350
        )
        error_label.pack(expand=True, padx=20, pady=20)
        
        # Botão de fechar
        close_button = ctk.CTkButton(
            error_window,
            text="Fechar",
            command=error_window.destroy
        )
        close_button.pack(pady=10)
    
    def create_widgets(self):
        """Create and arrange all GUI elements.
        
        Creates a clean, organized interface with:
        - URL input field
        - Download directory selection
        - Format and quality options
        - Download button
        - Downloads list
        - Status display
        """
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="YouTube Downloader",
            font=("Roboto", 24, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Content frame with consistent padding
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=0)
        
        # 1. URL Input Section
        url_label = ctk.CTkLabel(
            content_frame,
            text="Video URL:",
            font=("Roboto", 14, "bold"),
            anchor="w"
        )
        url_label.pack(fill="x", pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            content_frame,
            height=40,
            placeholder_text="Paste YouTube URL here..."
        )
        self.url_entry.pack(fill="x", pady=(0, 20))
        
        # 2. Download Directory Section
        dir_label = ctk.CTkLabel(
            content_frame,
            text="Save Location:",
            font=("Roboto", 14, "bold"),
            anchor="w"
        )
        dir_label.pack(fill="x", pady=(0, 5))
        
        dir_frame = ctk.CTkFrame(content_frame)
        dir_frame.pack(fill="x", pady=(0, 20))
        
        self.dir_entry = ctk.CTkEntry(dir_frame)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.dir_entry.insert(0, self.download_dir)
        
        browse_btn = ctk.CTkButton(
            dir_frame,
            text="Browse",
            width=100,
            command=self.browse_directory
        )
        browse_btn.pack(side="right")
        
        # 3. Format Options Section
        format_label = ctk.CTkLabel(
            content_frame,
            text="Download Options:",
            font=("Roboto", 14, "bold"),
            anchor="w"
        )
        format_label.pack(fill="x", pady=(0, 10))
        
        # Format selection frame
        format_frame = ctk.CTkFrame(content_frame)
        format_frame.pack(fill="x", pady=(0, 20))
        
        # Media Type Selection
        type_label = ctk.CTkLabel(
            format_frame,
            text="Type:",
            font=("Roboto", 13),
            width=80
        )
        type_label.pack(side="left", padx=10)
        
        self.format_type_var = tk.StringVar(value="video")
        self.format_type_var.trace('w', self.update_format_options)
        
        video_rb = ctk.CTkRadioButton(
            format_frame,
            text="Video",
            variable=self.format_type_var,
            value="video"
        )
        video_rb.pack(side="left", padx=10)
        
        audio_rb = ctk.CTkRadioButton(
            format_frame,
            text="Audio",
            variable=self.format_type_var,
            value="audio"
        )
        audio_rb.pack(side="left", padx=10)
        
        # Format Options Frame
        self.format_options_frame = ctk.CTkFrame(content_frame)
        self.format_options_frame.pack(fill="x", pady=(0, 20))
        
        # Format Combobox
        format_box_label = ctk.CTkLabel(
            self.format_options_frame,
            text="Format:",
            font=("Roboto", 13),
            width=80
        )
        format_box_label.pack(side="left", padx=10)
        
        self.format_var = tk.StringVar()
        self.format_combo = ctk.CTkComboBox(
            self.format_options_frame,
            width=200,
            variable=self.format_var
        )
        self.format_combo.pack(side="left", padx=10)
        
        # Quality Label
        quality_label = ctk.CTkLabel(
            self.format_options_frame,
            text="Quality:",
            font=("Roboto", 13),
            width=80
        )
        quality_label.pack(side="left", padx=10)
        
        # Quality Combobox
        self.quality_var = tk.StringVar()
        self.quality_combo = ctk.CTkComboBox(
            self.format_options_frame,
            width=120,
            values=["High", "Medium", "Low"],
            variable=self.quality_var
        )
        self.quality_combo.pack(side="left", padx=10)
        self.quality_combo.set("High")
        
        # Initialize format options
        self.update_format_options()
        
        # 4. Download Button
        self.download_btn = ctk.CTkButton(
            content_frame,
            text="Download",
            command=self.start_download,
            height=45,
            font=("Roboto", 14, "bold"),
            fg_color="#00a884",
            hover_color="#008f6c"
        )
        self.download_btn.pack(fill="x", pady=(0, 20))
        
        # 5. Downloads List
        list_label = ctk.CTkLabel(
            content_frame,
            text="Downloads:",
            font=("Roboto", 14, "bold"),
            anchor="w"
        )
        list_label.pack(fill="x", pady=(0, 5))
        
        self.downloads_list = ctk.CTkScrollableFrame(
            content_frame,
            height=200
        )
        self.downloads_list.pack(fill="both", expand=True)
        
        # 6. Status
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="Ready",
            font=("Roboto", 12)
        )
        self.status_label.pack(pady=(10, 0))
    
    def update_format_options(self, *args):
        """Update format options based on selected media type.
        
        Updates the format dropdown menu with appropriate options when
        the user switches between video and audio.
        
        Args:
            *args: Variable arguments (unused, required for tkinter trace)
        """
        format_type = self.format_type_var.get()
        
        if format_type == "video":
            formats = ["MP4", "WebM", "MKV"]
        else:
            formats = ["MP3", "AAC", "Opus"]
        
        self.format_combo.configure(values=formats)
        self.format_combo.set(formats[0])
    
    def get_format_name(self):
        """Generate format name for the downloader.
        
        Combines the selected format and quality into a format name
        that matches the downloader's format definitions.
        
        Returns:
            str: Format name (e.g., 'mp4_high', 'mp3_medium')
        """
        format_type = self.format_type_var.get()
        format_value = self.format_combo.get().lower()
        quality = self.quality_var.get().lower()
        
        return f"{format_value}_{quality}"
    
    def start_download(self):
        """Start the download process.
        
        Validates input, prepares download parameters, and starts
        the download in a background thread. Updates UI accordingly.
        """
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="Please enter a URL")
            return
        
        # Update download directory
        self.download_dir = self.dir_entry.get().strip()
        if not os.path.exists(self.download_dir):
            try:
                os.makedirs(self.download_dir)
            except Exception as e:
                self.status_label.configure(text=f"Error creating directory: {str(e)}")
                return
        
        try:
            # Update UI
            self.status_label.configure(text="Starting download...")
            self.download_btn.configure(state="disabled")
            
            # Create download entry
            download_frame = ctk.CTkFrame(self.downloads_list)
            download_frame.pack(fill="x", padx=10, pady=5)
            
            title_label = ctk.CTkLabel(
                download_frame,
                text=url,
                font=("Roboto", 12)
            )
            title_label.pack(side="left", padx=10)
            
            progress_label = ctk.CTkLabel(
                download_frame,
                text="0%",
                font=("Roboto", 12)
            )
            progress_label.pack(side="right", padx=10)
            
            # Prepare format info
            format_info = {
                'format_type': self.format_type_var.get(),
                'format_name': self.get_format_name()
            }
            
            # Start download
            thread = threading.Thread(
                target=self.download_media,
                args=(url, download_frame, progress_label, format_info)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
            self.download_btn.configure(state="normal")
    
    def download_media(self, url, frame, progress_label, format_info):
        """Handle the media download process.
        
        Args:
            url (str): YouTube URL to download from
            frame (CTkFrame): Frame displaying download progress
            progress_label (CTkLabel): Label for progress updates
            format_info (dict): Format and quality options
        """
        try:
            def progress_callback(progress):
                progress_label.configure(text=f"{progress:.1f}%")
            
            # Download
            self.downloader.download_media(
                url=url,
                output_path=Path(self.download_dir),
                format_info=format_info,
                progress_callback=progress_callback
            )
            
            # Update UI
            progress_label.configure(text="Done!")
            self.status_label.configure(text="Download completed!")
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
            if frame:
                frame.destroy()
        
        finally:
            self.download_btn.configure(state="normal")
    
    def browse_directory(self):
        """Open directory browser for save location selection.
        
        Opens a system file dialog for the user to choose where
        downloads should be saved. Updates the config when changed.
        """
        dir_path = filedialog.askdirectory(initialdir=self.download_dir)
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)
            self.download_dir = dir_path
            self.save_config()
    
    def load_config(self):
        """Load application configuration from file.
        
        Returns:
            dict: Configuration settings
        """
        config_path = Path(BASE_DIR) / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save current configuration to file."""
        config_path = Path(BASE_DIR) / "config.json"
        config = {
            'download_dir': self.download_dir
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

if __name__ == "__main__":
    app = DownloaderGUI()
    app.run()

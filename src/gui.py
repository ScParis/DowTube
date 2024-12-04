import os
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import sys

from .downloader import MediaDownloader, DownloadError
from .config import (
    FORMATS, DOWNLOADS_DIR, AUDIO_QUALITIES,
    VIDEO_QUALITIES, MAX_CONCURRENT_DOWNLOADS
)

class DownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("DowTube - YouTube Media Downloader")
        self.geometry("1000x700")
        
        # Inicializa o downloader
        self.downloader = MediaDownloader()
        self.active_downloads = {}
        self.scheduled_downloads = {}
        
        # Carrega ícones
        self.load_icons()
        
        # Configura a interface
        self.setup_gui()

    def load_icons(self):
        """Carrega os ícones do sistema."""
        icons_dir = Path(__file__).parent.parent / "assets" / "icons"
        self.icons = {
            "download": self.load_icon(icons_dir / "download.png"),
            "playlist": self.load_icon(icons_dir / "playlist.png"),
            "favorite": self.load_icon(icons_dir / "favorite.png"),
            "schedule": self.load_icon(icons_dir / "schedule.png"),
            "settings": self.load_icon(icons_dir / "settings.png")
        }

    def load_icon(self, path: Path) -> ImageTk.PhotoImage:
        """Carrega um ícone específico."""
        if path.exists():
            return ImageTk.PhotoImage(Image.open(path).resize((24, 24)))
        return None

    def setup_gui(self):
        """Configura a interface principal."""
        # Container principal
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Barra lateral
        self.sidebar = ctk.CTkFrame(self.main_container, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        
        # Botões da barra lateral
        self.create_sidebar_buttons()
        
        # Container de conteúdo
        self.content = ctk.CTkFrame(self.main_container)
        self.content.pack(side="right", fill="both", expand=True)
        
        # Tabs
        self.create_tabs()
        
        # Barra de status
        self.create_status_bar()

    def create_sidebar_buttons(self):
        """Cria os botões da barra lateral."""
        buttons = [
            ("Download", self.show_download_tab, "download"),
            ("Playlist", self.show_playlist_tab, "playlist"),
            ("Favoritos", self.show_favorites_tab, "favorite"),
            ("Agendamento", self.show_schedule_tab, "schedule"),
            ("Configurações", self.show_settings_tab, "settings")
        ]
        
        for text, command, icon in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                image=self.icons.get(icon),
                compound="left",
                anchor="w",
                height=40,
                corner_radius=10
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_tabs(self):
        """Cria as abas do sistema."""
        # Frame para as abas
        self.tab_view = ctk.CTkTabview(self.content)
        self.tab_view.pack(fill="both", expand=True)
        
        # Cria as abas
        self.create_download_tab()
        self.create_playlist_tab()
        self.create_favorites_tab()
        self.create_schedule_tab()
        self.create_settings_tab()

    def create_download_tab(self):
        """Cria a aba de download."""
        tab = self.tab_view.add("Download")
        
        # Frame de entrada
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # URL
        url_label = ctk.CTkLabel(input_frame, text="URL do YouTube:")
        url_label.pack(anchor="w", padx=5, pady=2)
        
        self.url_entry = ctk.CTkEntry(input_frame, width=400)
        self.url_entry.pack(fill="x", padx=5, pady=2)
        
        # Opções de formato
        format_frame = ctk.CTkFrame(tab)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        # Tipo de mídia
        media_label = ctk.CTkLabel(format_frame, text="Tipo de Mídia:")
        media_label.pack(side="left", padx=5)
        
        self.media_type = tk.StringVar(value="audio")
        audio_rb = ctk.CTkRadioButton(
            format_frame,
            text="Áudio",
            variable=self.media_type,
            value="audio",
            command=self.update_format_options
        )
        audio_rb.pack(side="left", padx=5)
        
        video_rb = ctk.CTkRadioButton(
            format_frame,
            text="Vídeo",
            variable=self.media_type,
            value="video",
            command=self.update_format_options
        )
        video_rb.pack(side="left", padx=5)
        
        # Formato
        self.format_var = tk.StringVar()
        self.format_combo = ctk.CTkComboBox(
            format_frame,
            variable=self.format_var,
            values=list(FORMATS["audio"].keys()),
            command=self.update_quality_options
        )
        self.format_combo.pack(side="left", padx=5)
        
        # Qualidade
        self.quality_var = tk.StringVar()
        self.quality_combo = ctk.CTkComboBox(
            format_frame,
            variable=self.quality_var,
            values=AUDIO_QUALITIES
        )
        self.quality_combo.pack(side="left", padx=5)
        
        # Botão de download
        download_btn = ctk.CTkButton(
            tab,
            text="Download",
            command=self.start_download,
            fg_color="green",
            hover_color="dark green"
        )
        download_btn.pack(pady=10)
        
        # Lista de downloads
        downloads_frame = ctk.CTkFrame(tab)
        downloads_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        downloads_label = ctk.CTkLabel(downloads_frame, text="Downloads Ativos:")
        downloads_label.pack(anchor="w", padx=5, pady=2)
        
        self.downloads_tree = ttk.Treeview(
            downloads_frame,
            columns=("url", "format", "progress", "status"),
            show="headings"
        )
        self.downloads_tree.heading("url", text="URL")
        self.downloads_tree.heading("format", text="Formato")
        self.downloads_tree.heading("progress", text="Progresso")
        self.downloads_tree.heading("status", text="Status")
        self.downloads_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def create_status_bar(self):
        """Cria a barra de status."""
        self.status_bar = ctk.CTkFrame(self)
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Pronto",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar,
            width=200,
            mode="determinate"
        )
        self.progress_bar.pack(side="right", padx=5)
        self.progress_bar.set(0)

    def show_download_tab(self):
        """Mostra a aba de download."""
        self.tab_view.set("Download")

    def show_playlist_tab(self):
        """Mostra a aba de playlist."""
        self.tab_view.set("Playlist")

    def show_favorites_tab(self):
        """Mostra a aba de favoritos."""
        self.tab_view.set("Favoritos")

    def show_schedule_tab(self):
        """Mostra a aba de agendamento."""
        self.tab_view.set("Agendamento")

    def show_settings_tab(self):
        """Mostra a aba de configurações."""
        self.tab_view.set("Configurações")

    def update_format_options(self):
        """Atualiza as opções de formato."""
        if self.media_type.get() == "audio":
            self.format_combo.configure(values=list(FORMATS["audio"].keys()))
        else:
            self.format_combo.configure(values=list(FORMATS["video"].keys()))

    def update_quality_options(self):
        """Atualiza as opções de qualidade."""
        if self.media_type.get() == "audio":
            self.quality_combo.configure(values=AUDIO_QUALITIES)
        else:
            self.quality_combo.configure(values=VIDEO_QUALITIES)

    def start_download(self):
        """Inicia o download."""
        url = self.url_entry.get()
        format_type = self.media_type.get()
        format = self.format_var.get()
        quality = self.quality_var.get()

        if url and format_type and format and quality:
            self.downloader.download(url, format_type, format, quality, self.update_progress)
        else:
            messagebox.showerror("Erro", "Preencha todos os campos")

    def update_progress(self, progress, status):
        """Atualiza o progresso."""
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)

    def create_playlist_tab(self):
        """Cria a aba de playlist."""
        tab = self.tab_view.add("Playlist")
        
        # Frame de entrada
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # URL
        url_label = ctk.CTkLabel(input_frame, text="URL da Playlist:")
        url_label.pack(anchor="w", padx=5, pady=2)
        
        self.playlist_url_entry = ctk.CTkEntry(input_frame, width=400)
        self.playlist_url_entry.pack(fill="x", padx=5, pady=2)
        
        # Opções de download
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        # Download todos os vídeos
        self.download_all_var = tk.BooleanVar(value=True)
        download_all_cb = ctk.CTkCheckBox(
            options_frame,
            text="Download todos os vídeos",
            variable=self.download_all_var
        )
        download_all_cb.pack(side="left", padx=5)
        
        # Botão de download
        download_btn = ctk.CTkButton(
            tab,
            text="Download",
            command=self.start_playlist_download,
            fg_color="green",
            hover_color="dark green"
        )
        download_btn.pack(pady=10)

    def start_playlist_download(self):
        """Inicia o download da playlist."""
        url = self.playlist_url_entry.get()
        download_all = self.download_all_var.get()

        if url:
            self.downloader.download_playlist(url, download_all, self.update_playlist_progress)
        else:
            messagebox.showerror("Erro", "Preencha o campo de URL")

    def update_playlist_progress(self, progress, status):
        """Atualiza o progresso da playlist."""
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)

    def create_favorites_tab(self):
        """Cria a aba de favoritos."""
        tab = self.tab_view.add("Favoritos")
        
        # Frame de entrada
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # URL
        url_label = ctk.CTkLabel(input_frame, text="URL do Vídeo:")
        url_label.pack(anchor="w", padx=5, pady=2)
        
        self.favorite_url_entry = ctk.CTkEntry(input_frame, width=400)
        self.favorite_url_entry.pack(fill="x", padx=5, pady=2)
        
        # Botão de adicionar
        add_btn = ctk.CTkButton(
            tab,
            text="Adicionar",
            command=self.add_favorite,
            fg_color="green",
            hover_color="dark green"
        )
        add_btn.pack(pady=10)

    def add_favorite(self):
        """Adiciona um vídeo aos favoritos."""
        url = self.favorite_url_entry.get()

        if url:
            self.downloader.add_favorite(url)
            self.favorite_url_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Preencha o campo de URL")

    def create_schedule_tab(self):
        """Cria a aba de agendamento."""
        tab = self.tab_view.add("Agendamento")
        
        # Frame de entrada
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # URL
        url_label = ctk.CTkLabel(input_frame, text="URL do Vídeo:")
        url_label.pack(anchor="w", padx=5, pady=2)
        
        self.schedule_url_entry = ctk.CTkEntry(input_frame, width=400)
        self.schedule_url_entry.pack(fill="x", padx=5, pady=2)
        
        # Data e hora
        datetime_frame = ctk.CTkFrame(tab)
        datetime_frame.pack(fill="x", padx=10, pady=5)
        
        date_label = ctk.CTkLabel(datetime_frame, text="Data:")
        date_label.pack(side="left", padx=5)
        
        self.schedule_date_entry = ctk.CTkEntry(datetime_frame, width=100)
        self.schedule_date_entry.pack(side="left", padx=5)
        
        time_label = ctk.CTkLabel(datetime_frame, text="Hora:")
        time_label.pack(side="left", padx=5)
        
        self.schedule_time_entry = ctk.CTkEntry(datetime_frame, width=100)
        self.schedule_time_entry.pack(side="left", padx=5)
        
        # Botão de agendar
        schedule_btn = ctk.CTkButton(
            tab,
            text="Agendar",
            command=self.schedule_download,
            fg_color="green",
            hover_color="dark green"
        )
        schedule_btn.pack(pady=10)

    def schedule_download(self):
        """Agenda um download."""
        url = self.schedule_url_entry.get()
        date = self.schedule_date_entry.get()
        time = self.schedule_time_entry.get()

        if url and date and time:
            self.downloader.schedule_download(url, date, time)
            self.schedule_url_entry.delete(0, tk.END)
            self.schedule_date_entry.delete(0, tk.END)
            self.schedule_time_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Preencha todos os campos")

    def create_settings_tab(self):
        """Cria a aba de configurações."""
        tab = self.tab_view.add("Configurações")
        
        # Frame de configurações
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Diretório de downloads
        dir_label = ctk.CTkLabel(settings_frame, text="Diretório de Downloads:")
        dir_label.pack(anchor="w", padx=5, pady=2)
        
        self.download_dir_entry = ctk.CTkEntry(settings_frame, width=400)
        self.download_dir_entry.pack(fill="x", padx=5, pady=2)
        
        # Botão de salvar
        save_btn = ctk.CTkButton(
            tab,
            text="Salvar",
            command=self.save_settings,
            fg_color="green",
            hover_color="dark green"
        )
        save_btn.pack(pady=10)

    def save_settings(self):
        """Salva as configurações."""
        dir = self.download_dir_entry.get()

        if dir:
            self.downloader.save_settings(dir)
            self.download_dir_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Preencha o campo de diretório")

if __name__ == "__main__":
    app = DownloaderGUI()
    app.run()

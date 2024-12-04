import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from src.downloader import MediaDownloader, DownloadError
from src.config import (
    FORMATS, THEMES, DOWNLOAD_SETTINGS, 
    PLAYLIST_SETTINGS, FAVORITES_DIR
)

class DownloaderGUI:
    def __init__(self):
        self.downloader = MediaDownloader()
        self.favorites = self.load_favorites()
        self.scheduled_downloads = []
        self.current_theme = "dark"
        self.setup_gui()

    def setup_gui(self):
        # Configuração da janela principal
        self.root = ctk.CTk()
        self.root.title("YouTube Downloader")
        self.root.geometry("1000x700")
        
        # Configuração do tema
        self.apply_theme("dark")

        # Menu principal
        self.create_menu()

        # Container principal com notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Abas
        self.download_tab = self.create_download_tab()
        self.playlist_tab = self.create_playlist_tab()
        self.favorites_tab = self.create_favorites_tab()
        self.schedule_tab = self.create_schedule_tab()
        self.settings_tab = self.create_settings_tab()

        # Barra de status
        self.status_bar = self.create_status_bar()

        # Atalhos de teclado
        self.bind_shortcuts()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo Download", command=self.new_download)
        file_menu.add_command(label="Abrir Pasta Downloads", command=self.open_downloads)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        # Menu Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Preferências", command=self.show_preferences)

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Documentação", command=self.show_docs)
        help_menu.add_command(label="Sobre", command=self.show_about)

    def create_download_tab(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Download")

        # URL Input com suporte a drag-and-drop
        url_frame = ctk.CTkFrame(tab)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        url_label = ctk.CTkLabel(url_frame, text="URL:")
        url_label.pack(side=tk.LEFT, padx=5)
        
        self.url_entry = ctk.CTkEntry(url_frame, width=400)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.drop_target_register(tk.DND_TEXT)
        self.url_entry.dnd_bind('<<Drop>>', self.handle_drop)

        # Seleção de formato
        format_frame = ctk.CTkFrame(tab)
        format_frame.pack(fill=tk.X, padx=10, pady=5)

        self.format_var = tk.StringVar(value="audio")
        audio_btn = ctk.CTkRadioButton(format_frame, text="Áudio", variable=self.format_var, value="audio")
        video_btn = ctk.CTkRadioButton(format_frame, text="Vídeo", variable=self.format_var, value="video")
        
        audio_btn.pack(side=tk.LEFT, padx=5)
        video_btn.pack(side=tk.LEFT, padx=5)

        # Qualidade
        self.quality_frame = ctk.CTkFrame(tab)
        self.quality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.format_combobox = ctk.CTkComboBox(self.quality_frame, values=list(FORMATS["audio"].keys()))
        self.quality_combobox = ctk.CTkComboBox(self.quality_frame, values=[])
        
        self.format_combobox.pack(side=tk.LEFT, padx=5)
        self.quality_combobox.pack(side=tk.LEFT, padx=5)

        # Botões de ação
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        preview_btn = ctk.CTkButton(button_frame, text="Preview", command=self.preview_media)
        download_btn = ctk.CTkButton(button_frame, text="Download", command=self.start_download)
        favorite_btn = ctk.CTkButton(button_frame, text="★", width=30, command=self.add_to_favorites)
        
        preview_btn.pack(side=tk.LEFT, padx=5)
        download_btn.pack(side=tk.LEFT, padx=5)
        favorite_btn.pack(side=tk.LEFT, padx=5)

        # Área de progresso
        self.progress_frame = ctk.CTkFrame(tab)
        self.progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        return tab

    def create_playlist_tab(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Playlist")

        # URL da Playlist
        playlist_frame = ctk.CTkFrame(tab)
        playlist_frame.pack(fill=tk.X, padx=10, pady=5)
        
        playlist_label = ctk.CTkLabel(playlist_frame, text="URL da Playlist:")
        playlist_label.pack(side=tk.LEFT, padx=5)
        
        self.playlist_entry = ctk.CTkEntry(playlist_frame, width=400)
        self.playlist_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Opções da Playlist
        options_frame = ctk.CTkFrame(tab)
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        self.download_all_var = tk.BooleanVar(value=PLAYLIST_SETTINGS["download_all"])
        download_all_cb = ctk.CTkCheckBox(options_frame, text="Baixar toda a playlist", 
                                        variable=self.download_all_var)
        download_all_cb.pack(side=tk.LEFT, padx=5)

        self.reverse_order_var = tk.BooleanVar(value=PLAYLIST_SETTINGS["reverse_order"])
        reverse_order_cb = ctk.CTkCheckBox(options_frame, text="Ordem reversa", 
                                         variable=self.reverse_order_var)
        reverse_order_cb.pack(side=tk.LEFT, padx=5)

        # Lista de vídeos
        self.playlist_listbox = tk.Listbox(tab, selectmode=tk.MULTIPLE)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Botões
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        load_btn = ctk.CTkButton(button_frame, text="Carregar Playlist", 
                               command=self.load_playlist)
        download_btn = ctk.CTkButton(button_frame, text="Download Selecionados", 
                                   command=self.download_selected)
        
        load_btn.pack(side=tk.LEFT, padx=5)
        download_btn.pack(side=tk.LEFT, padx=5)

        return tab

    def create_favorites_tab(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Favoritos")

        # Lista de favoritos
        self.favorites_listbox = tk.Listbox(tab)
        self.favorites_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Botões
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        download_btn = ctk.CTkButton(button_frame, text="Download", 
                                   command=self.download_favorite)
        remove_btn = ctk.CTkButton(button_frame, text="Remover", 
                                 command=self.remove_favorite)
        
        download_btn.pack(side=tk.LEFT, padx=5)
        remove_btn.pack(side=tk.LEFT, padx=5)

        # Carregar favoritos
        self.load_favorites_list()

        return tab

    def create_schedule_tab(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Agendamento")

        # Formulário de agendamento
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        url_label = ctk.CTkLabel(form_frame, text="URL:")
        url_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.schedule_url_entry = ctk.CTkEntry(form_frame, width=400)
        self.schedule_url_entry.pack(fill=tk.X, padx=5, pady=2)

        # Data e hora
        datetime_frame = ctk.CTkFrame(form_frame)
        datetime_frame.pack(fill=tk.X, padx=5, pady=2)

        self.date_entry = ctk.CTkEntry(datetime_frame, width=100, 
                                     placeholder_text="YYYY-MM-DD")
        self.time_entry = ctk.CTkEntry(datetime_frame, width=100, 
                                     placeholder_text="HH:MM")
        
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.time_entry.pack(side=tk.LEFT, padx=5)

        # Botão agendar
        schedule_btn = ctk.CTkButton(form_frame, text="Agendar Download", 
                                   command=self.schedule_download)
        schedule_btn.pack(pady=5)

        # Lista de downloads agendados
        self.schedule_listbox = tk.Listbox(tab)
        self.schedule_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        return tab

    def create_settings_tab(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Configurações")

        # Tema
        theme_frame = ctk.CTkFrame(tab)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Tema:")
        theme_label.pack(side=tk.LEFT, padx=5)
        
        self.theme_combobox = ctk.CTkComboBox(theme_frame, values=list(THEMES.keys()),
                                             command=self.apply_theme)
        self.theme_combobox.pack(side=tk.LEFT, padx=5)
        self.theme_combobox.set(self.current_theme)

        # Configurações de Download
        download_frame = ctk.CTkFrame(tab)
        download_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for key, value in DOWNLOAD_SETTINGS.items():
            var = tk.BooleanVar(value=value)
            cb = ctk.CTkCheckBox(download_frame, text=key.replace("_", " ").title(),
                               variable=var)
            cb.pack(anchor=tk.W, padx=5, pady=2)

        # Limite de Downloads
        limit_frame = ctk.CTkFrame(tab)
        limit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        limit_label = ctk.CTkLabel(limit_frame, text="Downloads Simultâneos:")
        limit_label.pack(side=tk.LEFT, padx=5)
        
        self.limit_spinbox = ttk.Spinbox(limit_frame, from_=1, to=10, width=5)
        self.limit_spinbox.pack(side=tk.LEFT, padx=5)
        self.limit_spinbox.set(os.cpu_count() or 2)

        return tab

    def create_status_bar(self):
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Pronto")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        return status_frame

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_download())
        self.root.bind("<Control-o>", lambda e: self.open_downloads())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-p>", lambda e: self.preview_media())
        self.root.bind("<Control-d>", lambda e: self.start_download())
        self.root.bind("<Control-f>", lambda e: self.add_to_favorites())

    def handle_drop(self, event):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, event.data)

    def load_favorites(self) -> Dict[str, Any]:
        try:
            with open(FAVORITES_DIR / "favorites.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_favorites(self):
        with open(FAVORITES_DIR / "favorites.json", "w") as f:
            json.dump(self.favorites, f, indent=4)

    def apply_theme(self, theme_name: str):
        self.current_theme = theme_name
        theme = THEMES[theme_name]
        
        if theme == "system":
            ctk.set_appearance_mode("system")
        else:
            ctk.set_appearance_mode("dark" if theme_name == "dark" else "light")
            self.root.configure(bg=theme["bg_color"])
            for widget in self.root.winfo_children():
                if isinstance(widget, (ctk.CTkFrame, ctk.CTkLabel, ctk.CTkButton)):
                    widget.configure(fg_color=theme["fg_color"])

    def update_status(self, message: str, progress: Optional[float] = None):
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar["value"] = progress

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DownloaderGUI()
    app.run()

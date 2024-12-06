"""YouTube Downloader GUI application."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional, Dict
import logging
from datetime import datetime

from src.core.downloader import MediaDownloader, DownloadOptions, DownloadError
from src.config.settings import (
    DOWNLOADS_DIR,
    VIDEO_FORMATS,
    AUDIO_FORMATS,
    VIDEO_QUALITIES,
    AUDIO_QUALITIES,
    ERROR_MESSAGES,
    PADDING,
    LOGS_DIR
)
from src.utils.utils import read_logs

class SlidingPanel(ctk.CTkFrame):
    """A sliding panel that can be shown/hidden."""
    
    def __init__(self, master, width=300, **kwargs):
        """Initialize the sliding panel.
        
        Args:
            master: Parent widget
            width: Panel width in pixels
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(master, width=width, height=master.winfo_height(), **kwargs)
        
        self.width = width
        self.shown = False
        
        # Configure initial position (hidden)
        self.place(relx=1.0, rely=0, relheight=1)
        
    def toggle(self):
        """Toggle panel visibility."""
        if self.shown:
            self.hide()
        else:
            self.show()
            
    def show(self):
        """Show the panel."""
        self.place(relx=1.0 - (self.width / self.master.winfo_width()), rely=0)
        self.shown = True
        
    def hide(self):
        """Hide the panel."""
        self.place(relx=1.0, rely=0)
        self.shown = False

class DownloaderGUI(ctk.CTk):
    """Main GUI window for YouTube Downloader application."""
    
    def __init__(self):
        super().__init__()
        self._setup_logging()
        self._initialize_gui()
        self._create_menu()
        self._create_main_layout()
        
        self.downloader = MediaDownloader()
        self.active_downloads: Dict[str, Dict] = {}
        self.progress_bar = ctk.CTkProgressBar(master=self, width=300)
        self.progress_bar.pack(pady=10)

    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _initialize_gui(self) -> None:
        """Initialize GUI settings and window properties."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("YouTube Downloader")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        
        self._configure_colors()
        
    def _configure_colors(self) -> None:
        """Configure custom colors for the GUI."""
        self.colors = {
            'bg': '#1c1c1c',
            'button': '#2962ff',
            'button_hover': '#1e88e5',
            'text': '#ffffff',
            'entry_bg': '#2d2d2d',
            'frame_bg': '#242424',
            'success': '#4caf50',
            'error': '#f44336'
        }
        
        self.configure(fg_color=self.colors['bg'])

    def _create_menu(self) -> None:
        """Create menu bar with help and logs buttons."""
        menu_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg']
        )
        menu_frame.pack(fill="x", padx=5, pady=5)
        
        # Help button
        help_button = ctk.CTkButton(
            menu_frame,
            text="?",
            width=30,
            command=self._show_help,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover']
        )
        help_button.pack(side="right", padx=5)
        
        # Logs button
        self.logs_button = ctk.CTkButton(
            menu_frame,
            text="📋 Logs",
            width=80,
            command=self._toggle_logs_panel,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover']
        )
        self.logs_button.pack(side="right", padx=5)

    def _create_main_layout(self) -> None:
        """Create main two-column layout."""
        # Main container
        main_container = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg']
        )
        main_container.pack(fill="both", expand=True, padx=PADDING['large'], 
                          pady=PADDING['large'])
        
        # Configure grid
        main_container.grid_columnconfigure(0, weight=3)  # Left column
        main_container.grid_columnconfigure(1, weight=2)  # Right column
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create columns
        self._create_left_column(main_container)
        self._create_right_column(main_container)
        
        # Create sliding logs panel
        self._create_logs_panel()
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            master=self,
            text="Cancelar Download",
            command=self.cancel_download,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover']
        )
        self.cancel_button.pack(pady=10)
        
        # Clear log button
        self.clear_log_button = ctk.CTkButton(
            master=self,
            text="Limpar Log",
            command=self.clear_log,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover']
        )
        self.clear_log_button.pack(pady=10)
        
        # Open logs folder button
        self.open_logs_button = ctk.CTkButton(
            master=self,
            text="Abrir Pasta de Logs",
            command=self.open_logs_folder,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover']
        )
        self.open_logs_button.pack(pady=10)

    def _create_left_column(self, parent) -> None:
        """Create left column with input controls."""
        left_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['frame_bg']
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, PADDING['medium']))
        
        # Title
        title = ctk.CTkLabel(
            left_frame,
            text="YouTube Downloader",
            font=("Roboto", 28, "bold"),
            text_color=self.colors['text']
        )
        title.pack(pady=(PADDING['large'], PADDING['large']))
        
        # URL Input
        url_label = ctk.CTkLabel(
            left_frame,
            text="Video URL:",
            font=("Roboto", 14, "bold"),
            text_color=self.colors['text']
        )
        url_label.pack(anchor="w", padx=PADDING['medium'])
        
        self.url_entry = ctk.CTkEntry(
            left_frame,
            height=40,
            placeholder_text="Paste YouTube URL here...",
            fg_color=self.colors['entry_bg'],
            text_color=self.colors['text'],
            placeholder_text_color='gray'
        )
        self.url_entry.pack(fill="x", padx=PADDING['medium'], 
                          pady=(PADDING['small'], PADDING['medium']))
        
        # Media Type Selection
        type_frame = ctk.CTkFrame(
            left_frame,
            fg_color="transparent"
        )
        type_frame.pack(fill="x", pady=PADDING['medium'])
        
        type_label = ctk.CTkLabel(
            type_frame,
            text="Type:",
            font=("Roboto", 14, "bold"),
            text_color=self.colors['text']
        )
        type_label.pack(side="left", padx=PADDING['medium'])
        
        self.type_var = tk.StringVar(value="video")
        
        video_rb = ctk.CTkRadioButton(
            type_frame,
            text="Video",
            variable=self.type_var,
            value="video",
            command=self._update_format_options,
            fg_color=self.colors['button'],
            text_color=self.colors['text']
        )
        video_rb.pack(side="left", padx=PADDING['medium'])
        
        audio_rb = ctk.CTkRadioButton(
            type_frame,
            text="Audio",
            variable=self.type_var,
            value="audio",
            command=self._update_format_options,
            fg_color=self.colors['button'],
            text_color=self.colors['text']
        )
        audio_rb.pack(side="left", padx=PADDING['medium'])
        
        # Format Selection
        format_label = ctk.CTkLabel(
            left_frame,
            text="Format:",
            font=("Roboto", 14, "bold"),
            text_color=self.colors['text']
        )
        format_label.pack(anchor="w", padx=PADDING['medium'], 
                         pady=(PADDING['medium'], 0))
        
        self.format_var = tk.StringVar(value="MP4")
        self.format_menu = ctk.CTkOptionMenu(
            left_frame,
            values=list(VIDEO_FORMATS.keys()),
            variable=self.format_var,
            fg_color=self.colors['button'],
            button_color=self.colors['button'],
            button_hover_color=self.colors['button_hover'],
            dropdown_fg_color=self.colors['frame_bg'],
            dropdown_hover_color=self.colors['button_hover']
        )
        self.format_menu.pack(fill="x", padx=PADDING['medium'], 
                            pady=(PADDING['small'], PADDING['medium']))
        
        # Quality Selection
        quality_label = ctk.CTkLabel(
            left_frame,
            text="Quality:",
            font=("Roboto", 14, "bold"),
            text_color=self.colors['text']
        )
        quality_label.pack(anchor="w", padx=PADDING['medium'])
        
        self.quality_var = tk.StringVar(value=VIDEO_QUALITIES[2])
        self.quality_menu = ctk.CTkOptionMenu(
            left_frame,
            values=VIDEO_QUALITIES,
            variable=self.quality_var,
            fg_color=self.colors['button'],
            button_color=self.colors['button'],
            button_hover_color=self.colors['button_hover'],
            dropdown_fg_color=self.colors['frame_bg'],
            dropdown_hover_color=self.colors['button_hover']
        )
        self.quality_menu.pack(fill="x", padx=PADDING['medium'], 
                             pady=(PADDING['small'], PADDING['medium']))
        
        # Directory Selection
        dir_button = ctk.CTkButton(
            left_frame,
            text="Change Download Directory",
            command=self._select_directory,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            height=40
        )
        dir_button.pack(fill="x", padx=PADDING['medium'], 
                       pady=PADDING['medium'])
        
        # Download Button
        self.download_button = ctk.CTkButton(
            left_frame,
            text="Download",
            command=self._start_download,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            height=50,
            font=("Roboto", 16, "bold")
        )
        self.download_button.pack(fill="x", padx=PADDING['medium'], 
                                pady=PADDING['medium'])

    def _create_right_column(self, parent) -> None:
        """Create right column with status and progress."""
        right_frame = ctk.CTkFrame(
            parent,
            fg_color=self.colors['frame_bg']
        )
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Status Header
        status_header = ctk.CTkLabel(
            right_frame,
            text="Download Status",
            font=("Roboto", 20, "bold"),
            text_color=self.colors['text']
        )
        status_header.pack(pady=PADDING['medium'])
        
        # Status Display
        self.status_text = ctk.CTkTextbox(
            right_frame,
            fg_color=self.colors['entry_bg'],
            text_color=self.colors['text']
        )
        self.status_text.pack(fill="both", expand=True, padx=PADDING['medium'], 
                            pady=PADDING['medium'])
        self.status_text.configure(state="disabled")

    def _create_logs_panel(self) -> None:
        """Create the sliding logs panel."""
        self.logs_panel = SlidingPanel(
            master=self,
            width=400,
            fg_color=("gray85", "gray20")
        )
        
        # Logs text area
        self.logs_text = ctk.CTkTextbox(
            master=self.logs_panel,
            wrap="word",
            font=("Courier", 12)
        )
        self.logs_text.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Update logs initially
        self._update_logs()
        
        # Schedule periodic log updates
        self.after(5000, self._update_logs)

    def _toggle_logs_panel(self) -> None:
        """Toggle the logs panel visibility."""
        self.logs_panel.toggle()
        if self.logs_panel.shown:
            self._refresh_logs()

    def _refresh_logs(self) -> None:
        """Refresh the logs display."""
        logs_content = read_logs()
        self.logs_text.configure(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.insert("1.0", logs_content)
        self.logs_text.configure(state="disabled")
        self.logs_text.see("end")

    def _update_format_options(self, *args) -> None:
        """Update format options based on selected media type."""
        media_type = self.type_var.get()
        
        if media_type == "video":
            self.format_menu.configure(values=list(VIDEO_FORMATS.keys()))
            self.format_var.set("MP4")
            self.quality_menu.configure(values=VIDEO_QUALITIES)
            self.quality_var.set(VIDEO_QUALITIES[2])
        else:
            self.format_menu.configure(values=list(AUDIO_FORMATS.keys()))
            self.format_var.set("MP3")
            self.quality_menu.configure(values=AUDIO_QUALITIES)
            self.quality_var.set(AUDIO_QUALITIES[0])

    def _show_help(self) -> None:
        """Show help window with usage instructions."""
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help")
        help_window.geometry("600x400")
        help_window.configure(fg_color=self.colors['bg'])
        
        help_text = ctk.CTkTextbox(
            help_window,
            fg_color=self.colors['frame_bg'],
            text_color=self.colors['text']
        )
        help_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_content = """
        YouTube Downloader - Help Guide
        
        1. How to Use:
           - Paste the YouTube video URL
           - Choose media type (Video or Audio)
           - Select desired format
           - Select quality
           - Click Download
        
        2. Supported Formats:
           - Video: MP4, WebM, MKV
           - Audio: MP3, AAC, Opus
        
        3. Error Logs:
           - Click the "📋 Logs" button to view logs
           - Each log entry includes timestamp
           - Click refresh to update logs
        
        4. Troubleshooting:
           - Check error logs
           - Ensure stable internet connection
           - Verify video availability
           - Check write permissions
        """
        
        help_text.insert("1.0", help_content)
        help_text.configure(state="disabled")

    def _select_directory(self) -> None:
        """Open directory selection dialog."""
        dir_path = filedialog.askdirectory(
            initialdir=DOWNLOADS_DIR,
            title="Select Download Directory"
        )
        if dir_path:
            self.download_dir = dir_path
            self._update_status(f"Download directory changed to: {dir_path}")

    def _start_download(self) -> None:
        """Initialize download process."""
        url = self.url_entry.get().strip()
        if not url:
            self._show_error(ERROR_MESSAGES['invalid_url'])
            return
            
        try:
            options = DownloadOptions(
                format=self.format_var.get(),
                quality=self.quality_var.get(),
                output_dir=getattr(self, 'download_dir', DOWNLOADS_DIR),
                convert_audio=(self.type_var.get() == "audio")
            )
            
            download_id = self.downloader.download(
                url, 
                options,
                self._update_progress
            )
            
            self.active_downloads[download_id] = {
                'url': url,
                'start_time': datetime.now()
            }
            
            self._update_status(f"Download started: {url}")
            self.download_button.configure(state="disabled")
            
        except DownloadError as e:
            self._show_error(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            self._show_error(ERROR_MESSAGES['download_failed'])

    def _update_progress(self, progress: float) -> None:
        """Update download progress display."""
        self._update_status(f"Download progress: {progress:.1f}%")
        if progress >= 100:
            self.download_button.configure(state="normal")
            self._update_status("Download completed!")

    def _update_status(self, message: str) -> None:
        """Update status display with new message."""
        self.status_text.configure(state="normal")
        self.status_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def _show_error(self, message: str) -> None:
        """Display error message."""
        self._update_status(f"Error: {message}")
        self.logger.error(message)
        messagebox.showerror("Error", message)

    def _update_logs(self):
        """Update logs display."""
        logs_content = read_logs()
        self.logs_text.configure(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.insert("1.0", logs_content)
        self.logs_text.configure(state="disabled")
        self.logs_text.see("end")
        self.after(5000, self._update_logs)

    def update_progress(self, current: int, total: int):
        """Update the progress bar based on current and total values."""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar.set(percentage)
        else:
            self.progress_bar.set(0)

    def cancel_download(self):
        """Cancel the ongoing download."""
        if self.downloader._current_download:
            download_id = self.downloader._current_download.id  # Obter o ID do download atual
            self.downloader.cancel(download_id)  # Passar o ID para o método de cancelamento
            logging.info("Download canceled by user.")
        else:
            logging.warning("No current download to cancel.")

    def clear_log(self):
        """Clear the log file."""
        log_file_path = os.path.join(LOGS_DIR, "youtube_downloader.log")
        open(log_file_path, 'w').close()  # Clear the log file
        logging.info("Log file cleared.")
        self.logs_text.configure(state="normal")
        self.logs_text.delete("1.0", "end")  # Clear the displayed logs
        self.logs_text.configure(state="disabled")
        messagebox.showinfo("Log Cleared", "The log file has been cleared.")

    def open_logs_folder(self):
        """Open the logs folder in the file explorer."""
        logs_folder_path = os.path.expanduser("~/.my-yt-down/logs/")
        os.system(f'xdg-open "{logs_folder_path}"')  # Open the logs folder in the file explorer
        logging.info("Opened logs folder.")

if __name__ == "__main__":
    app = DownloaderGUI()
    app.mainloop()

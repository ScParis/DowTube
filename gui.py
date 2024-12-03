import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from downloader import MediaDownloader, DownloadError
import threading
from config import FORMATS
import os

class DownloaderGUI:
    def __init__(self):
        self.downloader = MediaDownloader()
        self.setup_gui()

    def setup_gui(self):
        # Configuração da janela principal
        self.root = ctk.CTk()
        self.root.title("YouTube Downloader")
        self.root.geometry("800x600")
        
        # Configuração do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # URL Input
        self.url_frame = ctk.CTkFrame(self.main_frame)
        self.url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="URL do YouTube:")
        self.url_label.pack(side=tk.LEFT, padx=5)
        
        self.url_entry = ctk.CTkEntry(self.url_frame, width=500)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Pasta de destino
        self.folder_frame = ctk.CTkFrame(self.main_frame)
        self.folder_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Pasta de destino:")
        self.folder_label.pack(side=tk.LEFT, padx=5)
        
        self.folder_entry = ctk.CTkEntry(self.folder_frame, width=400)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.browse_button = ctk.CTkButton(
            self.folder_frame,
            text="Procurar",
            command=self.browse_folder
        )
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # Opções de formato
        self.format_frame = ctk.CTkFrame(self.main_frame)
        self.format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.format_label = ctk.CTkLabel(self.format_frame, text="Formato:")
        self.format_label.pack(side=tk.LEFT, padx=5)
        
        self.format_var = tk.StringVar(value="mp3")
        self.format_mp3 = ctk.CTkRadioButton(
            self.format_frame,
            text="MP3",
            variable=self.format_var,
            value="mp3",
            command=self.update_quality_options
        )
        self.format_mp3.pack(side=tk.LEFT, padx=20)
        
        self.format_mp4 = ctk.CTkRadioButton(
            self.format_frame,
            text="MP4",
            variable=self.format_var,
            value="mp4",
            command=self.update_quality_options
        )
        self.format_mp4.pack(side=tk.LEFT, padx=20)

        # Opções de qualidade
        self.quality_frame = ctk.CTkFrame(self.main_frame)
        self.quality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.quality_label = ctk.CTkLabel(self.quality_frame, text="Qualidade:")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        self.quality_var = tk.StringVar()
        self.quality_combo = ctk.CTkComboBox(
            self.quality_frame,
            values=list(FORMATS["mp3"].keys()),
            variable=self.quality_var,
            width=200
        )
        self.quality_combo.pack(side=tk.LEFT, padx=5)
        self.quality_combo.set(list(FORMATS["mp3"].keys())[0])

        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="")
        self.status_label.pack(fill=tk.X, padx=5)

        # Botões
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.download_button = ctk.CTkButton(
            self.button_frame,
            text="Iniciar Download",
            command=self.start_download
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancelar",
            command=self.cancel_download,
            state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def update_quality_options(self):
        format_type = self.format_var.get()
        self.quality_combo.configure(values=list(FORMATS[format_type].keys()))
        self.quality_combo.set(list(FORMATS[format_type].keys())[0])

    def update_progress(self, progress_text):
        if "[download]" in progress_text:
            try:
                percent = float(progress_text.split("%")[0].split()[-1])
                self.progress_bar.set(percent / 100)
                self.status_label.configure(text=progress_text.strip())
                self.root.update_idletasks()
            except (ValueError, IndexError):
                pass

    def start_download(self):
        url = self.url_entry.get().strip()
        output_dir = self.folder_entry.get().strip()
        format_choice = self.format_var.get()
        quality = self.quality_var.get()

        if not url or not output_dir:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        try:
            self.download_button.configure(state=tk.DISABLED)
            self.cancel_button.configure(state=tk.NORMAL)
            
            threading.Thread(
                target=self.download_thread,
                args=(url, output_dir, format_choice, quality),
                daemon=True
            ).start()
        
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.reset_gui()

    def download_thread(self, url, output_dir, format_choice, quality):
        try:
            self.downloader.download_playlist(
                url,
                output_dir,
                format_choice,
                quality,
                self.update_progress
            )
            self.root.after(0, self.download_complete)
        
        except DownloadError as e:
            self.root.after(0, lambda: self.show_error(str(e)))
        
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erro inesperado: {str(e)}"))
        
        finally:
            self.root.after(0, self.reset_gui)

    def download_complete(self):
        messagebox.showinfo("Sucesso", "Download concluído com sucesso!")

    def show_error(self, message):
        messagebox.showerror("Erro", message)

    def reset_gui(self):
        self.download_button.configure(state=tk.NORMAL)
        self.cancel_button.configure(state=tk.DISABLED)
        self.progress_bar.set(0)
        self.status_label.configure(text="")

    def cancel_download(self):
        self.downloader.cancel_downloads()
        self.reset_gui()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DownloaderGUI()
    app.run()

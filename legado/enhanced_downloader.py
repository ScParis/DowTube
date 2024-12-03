import subprocess
import os
import json
import re
import shutil
from tqdm import tqdm
from datetime import datetime, timedelta
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# Configuração de logging
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
logging.basicConfig(
    filename=os.path.join(LOG_PATH, "download.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constantes
VALID_URL_REGEX = r"^https?://(?:www\.)?youtube\.com/watch\?v=.+|^https?://(?:www\.)?youtube\.com/playlist\?list=.+"
FORMATS = {
    "MP3 (Alta Qualidade)": {"format": "mp3", "quality": "320K"},
    "MP3 (Média Qualidade)": {"format": "mp3", "quality": "192K"},
    "MP4 (1080p)": {"format": "mp4", "quality": "1080"},
    "MP4 (720p)": {"format": "mp4", "quality": "720"},
    "MP4 (480p)": {"format": "mp4", "quality": "480"}
}

def check_disk_space(path, required_space_mb=1000):
    """Verifica se há espaço em disco suficiente."""
    total, used, free = shutil.disk_usage(path)
    free_mb = free // (1024 * 1024)  # Converter para MB
    return free_mb >= required_space_mb

def validate_url(url):
    """Valida a URL do YouTube."""
    if not re.match(VALID_URL_REGEX, url):
        raise ValueError("URL inválida. Certifique-se de que é uma URL válida do YouTube.")
    return True

def get_media_info(url):
    """Obtém informações sobre o vídeo/playlist."""
    try:
        yt_dlp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "yt-dlp")
        result = subprocess.run(
            [yt_dlp_path, "--flat-playlist", "--dump-json", url],
            capture_output=True,
            text=True,
            check=True
        )
        return [json.loads(line) for line in result.stdout.splitlines()]
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro ao obter informações da mídia: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao processar informações da mídia: {e}")
        raise

def save_logs(log_data, filename):
    """Salva os logs em diferentes formatos."""
    os.makedirs(LOG_PATH, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"{filename}_{timestamp}"

    # JSON
    json_path = os.path.join(LOG_PATH, f"{base_filename}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

    # TXT
    txt_path = os.path.join(LOG_PATH, f"{base_filename}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=== Resumo do Download ===\n\n")
        for key, value in log_data.items():
            if key != "erros":
                f.write(f"{key}: {value}\n")
        if log_data.get("erros"):
            f.write("\n=== Erros ===\n\n")
            for error in log_data["erros"]:
                f.write(f"URL: {error['url']}\n")
                f.write(f"Erro: {error['mensagem']}\n\n")

    # HTML
    html_path = os.path.join(LOG_PATH, f"{base_filename}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("""
        <html>
        <head>
            <title>Relatório de Download</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; }
                th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .error { color: red; }
            </style>
        </head>
        <body>
        """)
        f.write("<h1>Relatório de Download</h1>")
        f.write("<table>")
        for key, value in log_data.items():
            if key != "erros":
                f.write(f"<tr><th>{key}</th><td>{value}</td></tr>")
        f.write("</table>")
        
        if log_data.get("erros"):
            f.write("<h2>Erros</h2>")
            for error in log_data["erros"]:
                f.write(f"<div class='error'>")
                f.write(f"<p><strong>URL:</strong> {error['url']}</p>")
                f.write(f"<p><strong>Erro:</strong> {error['mensagem']}</p>")
                f.write("</div><hr>")
        f.write("</body></html>")

class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x400")
        self.setup_gui()

    def setup_gui(self):
        # Estilo
        style = ttk.Style()
        style.configure("TButton", padding=5)
        style.configure("TEntry", padding=5)

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # URL
        ttk.Label(main_frame, text="URL do YouTube:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Pasta de destino
        ttk.Label(main_frame, text="Pasta de destino:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.folder_entry = ttk.Entry(main_frame, width=40)
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_folder).grid(row=1, column=2, pady=5)

        # Formato
        ttk.Label(main_frame, text="Formato:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar()
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var, values=list(FORMATS.keys()))
        format_combo.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        format_combo.set(list(FORMATS.keys())[0])

        # Progresso
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Status
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Botão de download
        self.download_button = ttk.Button(main_frame, text="Iniciar Download", command=self.start_download)
        self.download_button.grid(row=5, column=0, columnspan=3, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()

    def start_download(self):
        url = self.url_entry.get().strip()
        output_folder = self.folder_entry.get().strip()
        format_choice = self.format_var.get()

        if not url or not output_folder:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        try:
            validate_url(url)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        if not check_disk_space(output_folder):
            messagebox.showerror("Erro", "Espaço em disco insuficiente (mínimo 1GB necessário)")
            return

        self.download_button.config(state="disabled")
        threading.Thread(target=self.download_media, args=(url, output_folder, format_choice), daemon=True).start()

    def download_media(self, url, output_folder, format_choice):
        try:
            os.makedirs(output_folder, exist_ok=True)
            start_time = datetime.now()
            format_info = FORMATS[format_choice]

            # Configurar comando base
            yt_dlp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "yt-dlp")
            command = [yt_dlp_path, "--output", f"{output_folder}/%(title)s.%(ext)s"]

            if format_info["format"] == "mp3":
                command.extend([
                    "-x",
                    "--audio-format", "mp3",
                    "--audio-quality", format_info["quality"]
                ])
            else:
                command.extend([
                    "-f", f"bestvideo[height<={format_info['quality']}]+bestaudio",
                    "--merge-output-format", "mp4"
                ])

            command.append(url)

            # Obter informações da mídia
            media_info = get_media_info(url)
            total_items = len(media_info)
            
            self.update_status(f"Iniciando download de {total_items} item(s)...")
            
            success_count = 0
            error_logs = []

            for i, item in enumerate(media_info, 1):
                try:
                    self.progress_var.set((i / total_items) * 100)
                    self.update_status(f"Baixando item {i} de {total_items}...")
                    
                    process = subprocess.run(command + [item["url"]], 
                                          capture_output=True, 
                                          text=True, 
                                          check=True)
                    success_count += 1
                except subprocess.CalledProcessError as e:
                    error_logs.append({
                        "url": item["url"],
                        "mensagem": str(e)
                    })
                    logging.error(f"Erro no download: {e}")

            # Gerar relatório
            end_time = datetime.now()
            elapsed_time = end_time - start_time
            
            log_data = {
                "Data e hora de início": start_time.strftime('%d/%m/%Y %H:%M:%S'),
                "Data e hora de fim": end_time.strftime('%d/%m/%Y %H:%M:%S'),
                "Tempo total": str(timedelta(seconds=elapsed_time.total_seconds())),
                "Total de itens": total_items,
                "Downloads com sucesso": success_count,
                "Erros": len(error_logs),
                "Formato": format_choice,
                "erros": error_logs
            }

            save_logs(log_data, "download_report")
            
            self.update_status("Download concluído!")
            messagebox.showinfo("Concluído", 
                              f"Download finalizado!\nSucesso: {success_count}\nErros: {len(error_logs)}")
        
        except Exception as e:
            logging.exception("Erro durante o download")
            messagebox.showerror("Erro", f"Erro durante o download: {str(e)}")
        
        finally:
            self.download_button.config(state="normal")
            self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = DownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

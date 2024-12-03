import subprocess
import os
import json
import re
from tqdm import tqdm
from datetime import datetime, timedelta
import logging

# Configuração de logging para mensagens mais detalhadas
logging.basicConfig(filename="download.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LOG_PATH = "/home/piperun/my_yt_down/logs"
VALID_URL_REGEX = r"^https?://(?:www\.)?youtube\.com/watch\?v=.+|^https?://(?:www\.)?youtube\.com/playlist\?list=.+"

def save_logs(log_data, filename):
    """
    Salva os logs em diferentes formatos (.txt, .html, .json).

    Args:
        log_data: Dicionário com os dados dos logs.
        filename: Nome base do arquivo (sem extensão).
    """
    os.makedirs(LOG_PATH, exist_ok=True)

    # Salvar em formato JSON
    json_path = os.path.join(LOG_PATH, f"{filename}.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(log_data, json_file, indent=4, ensure_ascii=False)

    # Salvar em formato TXT
    txt_path = os.path.join(LOG_PATH, f"{filename}.txt")
    with open(txt_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(f"Resumo do Download\n")
        txt_file.write("=" * 30 + "\n")
        for key, value in log_data.items():
            txt_file.write(f"{key}: {value}\n")
        txt_file.write("\nErros Detalhados\n")
        txt_file.write("=" * 30 + "\n")
        for error in log_data.get("erros", []):
            txt_file.write(f"URL: {error['url']}\n")
            txt_file.write(f"Erro: {error['mensagem']}\n\n")

    # Salvar em formato HTML
    html_path = os.path.join(LOG_PATH, f"{filename}.html")
    with open(html_path, "w", encoding="utf-8") as html_file:
        html_file.write("<html><head><title>Resumo do Download</title></head><body>")
        html_file.write("<h1>Resumo do Download</h1>")
        html_file.write("<table border='1'><tr><th>Item</th><th>Valor</th></tr>")
        for key, value in log_data.items():
            if key != "erros":
                html_file.write(f"<tr><td>{key}</td><td>{value}</td></tr>")
        html_file.write("</table>")
        html_file.write("<h2>Erros Detalhados</h2>")
        for error in log_data.get("erros", []):
            html_file.write("<p><strong>URL:</strong> " + error["url"] + "</p>")
            html_file.write("<p><strong>Erro:</strong> " + error["mensagem"] + "</p><hr>")
        html_file.write("</body></html>")


def download_media(url, output_folder, format_choice):
    os.makedirs(output_folder, exist_ok=True)
    start_time = datetime.now()

    # Validação da URL
    if not re.match(VALID_URL_REGEX, url):
        print("URL inválida. Certifique-se de que é uma URL do YouTube.")
        logging.error(f"URL inválida: {url}")
        return

    print(f"Início do download: {start_time.strftime('%d/%m/%Y %H:%M:%S')}")

    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--dump-json", url],
            capture_output=True,
            text=True,
            check=True
        )
        playlist_info = [json.loads(line) for line in result.stdout.splitlines()]
        total_videos = len(playlist_info)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Erro ao obter informações do vídeo/playlist: {e}")
        logging.exception(f"Erro ao obter informações: {e}")
        return

    print(f"Total de vídeos/músicas encontrados: {total_videos}")

    command_base = [
        "yt-dlp",
        "--output", f"{output_folder}/%(title)s.%(ext)s"
    ]

    if format_choice == "mp3":
        command_base += ["-x", "--audio-format", "mp3"]
    elif format_choice == "mp4":
        command_base += ["-f", "bestvideo+bestaudio", "--merge-output-format", "mp4"]
    else:
        print("Formato inválido. Escolha entre 'mp3' ou 'mp4'.")
        return

    total_downloaded = 0
    total_errors = 0
    error_logs = []

    with tqdm(total=total_videos, desc="Progresso Geral", unit="vídeo(s)/música(s)") as pbar_geral:
        # Aqui vamos usar diretamente a URL original ao invés de tentar extrair de playlist_info
        command = command_base + [url]
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in process.stdout:
                if "[download] Destination:" in line:
                    pbar_geral.set_description(f"Baixando: {line.split(': ')[1].strip()}")
                elif "[download]" in line and "%" in line and "of" in line and "at" in line:
                    pbar_geral.set_postfix_str(line.split("] ")[1].strip())

            process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
            
            pbar_geral.update(1)
            total_downloaded += 1

        except Exception as e:
            total_errors += 1
            error_logs.append({"url": url, "mensagem": str(e)})
            logging.exception(f"Erro ao baixar {url}: {e}")


    end_time = datetime.now()
    elapsed_time = end_time - start_time

    # Resumo dos resultados
    log_data = {
        "Data e hora de início": start_time.strftime('%d/%m/%Y %H:%M:%S'),
        "Data e hora de fim": end_time.strftime('%d/%m/%Y %H:%M:%S'),
        "Tempo total": str(timedelta(seconds=elapsed_time.total_seconds())),
        "Total de músicas": total_videos,
        "Músicas baixadas com sucesso": total_downloaded,
        "Erros durante o download": total_errors,
        "erros": error_logs
    }

    # Salvar logs
    save_logs(log_data, "download_log")

    print("\nResumo do Download:")
    for key, value in log_data.items():
        if key != "erros":
            print(f"{key}: {value}")


if __name__ == "__main__":
    url = input("Insira o link do vídeo ou playlist do YouTube: ")
    output_folder = input("Insira o caminho da pasta onde deseja salvar os arquivos: ")
    format_choice = input("Escolha o formato para download (mp3 ou mp4): ").lower()

    download_media(url, output_folder, format_choice)
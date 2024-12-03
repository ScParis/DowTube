import subprocess
import os
from tqdm import tqdm

def download_media(url, output_folder, format_choice):
    """
    Baixa mídia de um vídeo ou playlist do YouTube no formato escolhido e salva em uma pasta específica.
    
    Args:
        url: O URL do vídeo ou playlist do YouTube.
        output_folder: O caminho da pasta onde o arquivo será salvo.
        format_choice: O formato escolhido pelo usuário (mp3 ou mp4).
    """
    # Cria a pasta se ela não existir
    os.makedirs(output_folder, exist_ok=True)

    # Configurações do comando yt-dlp
    if format_choice == "mp3":
        command = [
            "yt-dlp",
            "-x",  # Extrai apenas o áudio
            "--audio-format", "mp3",  # Converte para MP3
            "--output", f"{output_folder}/%(title)s.%(ext)s",  # Salva o arquivo na pasta especificada
            "--ignore-errors",  # Ignora erros para continuar os downloads
            url
        ]
    elif format_choice == "mp4":
        command = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio",  # Melhor qualidade de vídeo e áudio
            "--merge-output-format", "mp4",  # Converte para MP4
            "--output", f"{output_folder}/%(title)s.%(ext)s",
            "--ignore-errors",
            url
        ]
    else:
        print("Formato inválido. Escolha entre 'mp3' ou 'mp4'.")
        return

    # Contadores de progresso e erros
    total_downloaded = 0
    total_errors = 0

    # Barra de progresso
    try:
        with tqdm(total=1, desc="Progresso", unit="música(s)") as pbar:
            subprocess.run(command, check=True)
            total_downloaded += 1
            pbar.update(1)
    except subprocess.CalledProcessError as e:
        total_errors += 1
        print(f"Erro ao baixar: {e}")

    # Resumo final
    print("\nResumo do Download:")
    print(f"Total de músicas: {total_downloaded + total_errors}")
    print(f"Músicas baixadas com sucesso: {total_downloaded}")
    print(f"Erros durante o download: {total_errors}")


if __name__ == "__main__":
    # Solicita o link do vídeo ou playlist
    url = input("Insira o link do vídeo ou playlist do YouTube: ")

    # Solicita a pasta de saída
    output_folder = input("Insira o caminho da pasta onde deseja salvar os arquivos: ")

    # Solicita o formato desejado
    format_choice = input("Escolha o formato para download (mp3 ou mp4): ").lower()

    # Faz o download
    download_media(url, output_folder, format_choice)

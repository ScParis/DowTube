import subprocess
import os

def download_media(url, output_folder, format_choice):
    """Baixa mídia de um vídeo do YouTube no formato escolhido e salva em uma pasta específica.

    Args:
        url: O URL do vídeo do YouTube.
        output_folder: O caminho da pasta onde o arquivo será salvo.
        format_choice: O formato escolhido pelo usuário (mp3 ou mp4).
    """
    # Cria a pasta se ela não existir
    os.makedirs(output_folder, exist_ok=True)

    # Configurações para o formato
    if format_choice == "mp3":
        command = [
            "yt-dlp",
            "-x",  # Extrair apenas o áudio
            "--audio-format", "mp3",  # Converter para MP3
            "--output", f"{output_folder}/%(title)s.%(ext)s",  # Salvar com título como nome do arquivo
            url
        ]
    elif format_choice == "mp4":
        command = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio",  # Baixar melhor vídeo e áudio combinados
            "--merge-output-format", "mp4",  # Salvar como MP4
            "--output", f"{output_folder}/%(title)s.%(ext)s",
            url
        ]
    else:
        print("Formato inválido. Escolha entre 'mp3' ou 'mp4'.")
        return

    try:
        # Executa o comando yt-dlp
        subprocess.run(command, check=True)
        print(f"Download concluído com sucesso! O arquivo foi salvo em {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao baixar a mídia: {e}")
    except FileNotFoundError:
        print("Erro: yt-dlp não está instalado ou não foi encontrado. Instale-o com 'pip install yt-dlp'.")

if __name__ == "__main__":
    # Solicita o link do vídeo
    url = input("Insira o link do vídeo do YouTube: ")

    # Solicita a pasta de saída
    output_folder = input("Insira o caminho da pasta onde deseja salvar o arquivo (ou digite 'nova' para criar uma nova pasta): ")
    if output_folder.lower() == "nova":
        output_folder = input("Digite o nome da nova pasta: ")
        output_folder = os.path.join(os.getcwd(), output_folder)
        print(f"Pasta {output_folder} será criada para o download.")

    # Solicita o formato desejado
    format_choice = input("Escolha o formato para download (mp3 ou mp4): ").lower()

    # Faz o download
    download_media(url, output_folder, format_choice)

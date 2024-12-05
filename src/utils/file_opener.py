import os
import platform
import subprocess
from pathlib import Path

def get_logs_dir():
    """Retorna o diretório de logs."""
    return Path.home() / '.my-yt-down' / 'logs'

def open_logs_directory():
    """
    Abre o diretório de logs no explorador de arquivos padrão do sistema.
    Cria o diretório se não existir.
    
    Returns:
        bool: True se abriu com sucesso, False caso contrário
    """
    logs_dir = get_logs_dir()
    
    # Criar diretório se não existir
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Detectar sistema operacional
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            subprocess.run(['open', str(logs_dir)])
        elif system == 'linux':
            # Tentar diferentes comandos comuns em ordem
            commands = [
                ['xdg-open', str(logs_dir)],  # Padrão Linux
                ['gnome-open', str(logs_dir)],  # GNOME
                ['kde-open', str(logs_dir)],   # KDE
                ['exo-open', str(logs_dir)],   # XFCE
                ['pcmanfm', str(logs_dir)]     # LXDE/LXQt
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd)
                    return True
                except FileNotFoundError:
                    continue
                    
            # Se nenhum comando funcionou, tentar o último recurso
            os.system(f'x-terminal-emulator -e "cd {str(logs_dir)} && ls -la"')
        else:
            raise OSError(f"Sistema operacional não suportado: {system}")
            
        return True
        
    except Exception as e:
        print(f"Erro ao abrir diretório de logs: {e}")
        return False

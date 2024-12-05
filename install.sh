#!/bin/bash

# Função para verificar se um comando existe
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# Função para detectar o sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/redhat-release ]; then
        echo "redhat"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    elif [ -f /etc/SuSE-release ] || [ -f /etc/opensuse-release ]; then
        echo "suse"
    else
        echo "unknown"
    fi
}

# Função para instalar dependências do sistema
install_system_dependencies() {
    echo "Verificando dependências do sistema..."
    
    OS=$(detect_os)
    case $OS in
        "macos")
            if ! check_command "brew"; then
                echo "Homebrew não encontrado. Instalando..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python@3.12 ffmpeg
            brew install --cask tcl-tk
            ;;
        "debian")
            sudo apt-get update
            sudo apt-get install -y python3-dev python3-tk python3-pip ffmpeg dpkg-dev
            ;;
        "redhat")
            sudo dnf install -y python3-devel python3-tkinter ffmpeg
            ;;
        "arch")
            sudo pacman -S --noconfirm python python-tkinter ffmpeg
            ;;
        "suse")
            sudo zypper install -y python3-devel python3-tk python3-pip ffmpeg
            ;;
        *)
            echo "Sistema operacional não suportado"
            exit 1
            ;;
    esac
}

# Função para criar ambiente virtual
setup_virtual_env() {
    echo "Configurando ambiente virtual..."
    
    # Criar e ativar ambiente virtual
    python3 -m venv venv
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências
    pip install -r requirements.txt
}

# Função para criar pacote .deb (apenas Linux Debian/Ubuntu)
create_deb_package() {
    echo "Criando pacote .deb..."
    
    # Instalar pyinstaller se necessário
    pip install pyinstaller
    
    # Criar executável com pyinstaller
    pyinstaller --onefile \
                --name my-yt-down \
                --add-data "src:src" \
                --hidden-import tqdm \
                --hidden-import yt_dlp \
                --hidden-import ffmpeg \
                --hidden-import schedule \
                --hidden-import notify_py \
                --hidden-import psutil \
                main.py

    # Criar estrutura de diretórios para o pacote .deb
    rm -rf debian/usr/local/bin/*
    rm -rf debian/usr/share/applications/*
    rm -rf debian/usr/share/icons/my-yt-down/*
    
    mkdir -p debian/usr/local/bin
    mkdir -p debian/usr/share/applications
    mkdir -p debian/usr/share/icons/my-yt-down
    
    # Copiar arquivos
    cp dist/my-yt-down debian/usr/local/bin/
    cp my-yt-down.desktop debian/usr/share/applications/
    cp icons/my-yt-down.png debian/usr/share/icons/my-yt-down/
    
    # Definir permissões
    chmod 755 debian/usr/local/bin/my-yt-down
    chmod 644 debian/usr/share/applications/my-yt-down.desktop
    chmod 644 debian/usr/share/icons/my-yt-down/my-yt-down.png
    
    # Criar pacote .deb
    dpkg-deb --build debian my-yt-down.deb
    
    echo "Pacote .deb criado com sucesso!"
}

# Menu principal
OS=$(detect_os)
echo "Instalador do YouTube Downloader"

PS3="Escolha uma opção: "
options=("Instalação completa (ambiente virtual + dependências)" "Criar pacote .deb" "Sair")
select opt in "${options[@]}"
do
    case $opt in
        "Instalação completa (ambiente virtual + dependências)")
            install_system_dependencies
            setup_virtual_env
            if [ "$OS" = "debian" ]; then
                create_deb_package
                sudo dpkg -i my-yt-down.deb
            fi
            echo "Instalação completa!"
            break
            ;;
        "Criar pacote .deb")
            if [ "$OS" = "debian" ]; then
                install_system_dependencies
                setup_virtual_env
                create_deb_package
            else
                echo "Esta opção só está disponível para sistemas Debian/Ubuntu"
            fi
            break
            ;;
        "Sair")
            break
            ;;
        *) 
            echo "Opção inválida"
            ;;
    esac
done

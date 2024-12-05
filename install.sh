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
            echo "Sistema operacional não reconhecido."
            echo "Por favor, instale python3-dev, python3-tk, ffmpeg manualmente para sua distribuição"
            exit 1
            ;;
    esac
}

# Função para criar ambiente virtual
setup_virtual_env() {
    echo "Configurando ambiente virtual..."
    
    # Criar ambiente virtual se não existir
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    if [[ "$OSTYPE" == "darwin"* ]]; then
        source venv/bin/activate
    else
        source venv/bin/activate
    fi
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Instalar dependências Python
    pip install -r requirements.txt
}

# Função para criar pacote .deb (apenas Linux Debian/Ubuntu)
create_deb_package() {
    if [ "$(detect_os)" != "debian" ]; then
        echo "A criação de pacote .deb só é suportada em sistemas Debian/Ubuntu"
        exit 1
    fi
    
    echo "Criando pacote .deb..."
    
    # Instalar pyinstaller se necessário
    pip install pyinstaller
    
    # Criar diretórios necessários
    mkdir -p debian/DEBIAN
    mkdir -p debian/usr/local/bin
    mkdir -p debian/usr/lib/my-yt-down
    mkdir -p debian/usr/share/applications
    mkdir -p debian/usr/share/icons/hicolor/256x256/apps
    
    # Gerar executável com PyInstaller
    pyinstaller --onedir \
        --name my-yt-down \
        --add-data "src:src" \
        --add-data "config.json:." \
        --hidden-import PIL \
        --hidden-import customtkinter \
        --hidden-import tqdm \
        --hidden-import yt_dlp \
        --hidden-import requests \
        --hidden-import ffmpeg \
        --hidden-import schedule \
        --hidden-import notify_py \
        --hidden-import psutil \
        main.py
    
    # Copiar arquivos para a estrutura do pacote
    cp -r dist/my-yt-down/* debian/usr/lib/my-yt-down/
    
    # Criar script wrapper
    cat > debian/usr/local/bin/my-yt-down << 'EOF'
#!/bin/bash
cd /usr/lib/my-yt-down
./my-yt-down "$@"
EOF
    
    chmod +x debian/usr/local/bin/my-yt-down
    
    # Criar arquivo .desktop
    cat > debian/usr/share/applications/my-yt-down.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=YouTube Downloader
GenericName=YouTube Video Downloader
Comment=Download videos and audio from YouTube
Exec=/usr/local/bin/my-yt-down
Icon=my-yt-down
Terminal=false
Categories=AudioVideo;Network;
Keywords=youtube;download;video;audio;
StartupNotify=true
StartupWMClass=my-yt-down
EOF
    
    # Criar arquivo de controle
    cat > debian/DEBIAN/control << 'EOF'
Package: my-yt-down
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.12), python3-tk, python3-pip, ffmpeg, libpython3.12, python3-pil
Maintainer: Your Name <your.email@example.com>
Description: YouTube Video Downloader
 A simple and efficient YouTube video downloader
 with a graphical user interface.
 Supports video and audio downloads with various quality options.
EOF
    
    # Criar pacote
    dpkg-deb --build debian my-yt-down.deb
    
    echo "Pacote .deb criado com sucesso!"
}

# Menu principal
OS=$(detect_os)
echo "Instalador do YouTube Downloader"

if [ "$OS" = "debian" ]; then
    echo "1. Instalação completa (ambiente virtual + dependências)"
    echo "2. Criar pacote .deb"
    echo "3. Sair"
    read -p "Escolha uma opção (1-3): " option
    
    case $option in
        1)
            install_system_dependencies
            setup_virtual_env
            echo "Instalação completa!"
            ;;
        2)
            install_system_dependencies
            setup_virtual_env
            create_deb_package
            ;;
        3)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida"
            exit 1
            ;;
    esac
else
    echo "1. Instalação completa (ambiente virtual + dependências)"
    echo "2. Sair"
    read -p "Escolha uma opção (1-2): " option
    
    case $option in
        1)
            install_system_dependencies
            setup_virtual_env
            echo "Instalação completa!"
            ;;
        2)
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo "Opção inválida"
            exit 1
            ;;
    esac
fi

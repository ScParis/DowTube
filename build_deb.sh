#!/bin/bash

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Instalar dependências do sistema
echo "Instalando dependências do sistema..."
apt-get update
apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    tk-dev \
    ffmpeg \
    dpkg-dev \
    imagemagick

# Verificar instalação do Tkinter
echo "Verificando instalação do Tkinter..."
python3 -c "import tkinter" || {
    echo "Erro: Tkinter não está instalado corretamente"
    echo "Tentando reinstalar..."
    apt-get install --reinstall python3-tk
    python3 -c "import tkinter" || {
        echo "Erro: Falha ao instalar Tkinter"
        exit 1
    }
}

# Limpar diretórios anteriores
rm -rf build/ dist/ debian/

# Criar estrutura de diretórios
mkdir -p debian/DEBIAN
mkdir -p debian/usr/local/bin
mkdir -p debian/usr/lib/my-yt-down
mkdir -p debian/usr/share/applications
mkdir -p debian/usr/share/icons/hicolor/256x256/apps
mkdir -p debian/usr/share/pixmaps

# Criar e ativar ambiente virtual temporário
echo "Criando ambiente virtual..."
python3 -m venv build_venv
source build_venv/bin/activate

# Instalar dependências no ambiente virtual
echo "Instalando dependências Python..."
pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt
pip install pyinstaller

# Verificar se todas as dependências foram instaladas
echo "Verificando dependências instaladas..."
python3 -c "
import pkg_resources
import sys
required = [l.strip().split('>=')[0] for l in open('requirements.txt')]
installed = [pkg.key for pkg in pkg_resources.working_set]
missing = [pkg for pkg in required if pkg.lower() not in [p.lower() for p in installed]]
if missing:
    print('Erro: Dependências faltando:', missing)
    sys.exit(1)
"

# Gerar executável com configurações específicas para Tkinter
echo "Gerando executável..."
pyinstaller --onedir \
    --name my-yt-down \
    --add-data "src:src" \
    --add-data "config.json:." \
    --hidden-import PIL \
    --hidden-import PIL._tkinter_finder \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.messagebox \
    --hidden-import _tkinter \
    --hidden-import customtkinter \
    --hidden-import tqdm \
    --hidden-import yt_dlp \
    --hidden-import requests \
    --hidden-import ffmpeg \
    --hidden-import schedule \
    --hidden-import notify_py \
    --hidden-import psutil \
    --collect-all tkinter \
    --collect-all customtkinter \
    main.py

# Desativar ambiente virtual
deactivate

# Copiar arquivos para a estrutura debian
cp -r dist/my-yt-down/* debian/usr/lib/my-yt-down/
cp src/assets/icon.png debian/usr/share/icons/hicolor/256x256/apps/my-yt-down.png
cp src/assets/icon.png debian/usr/share/pixmaps/my-yt-down.png

# Definir permissões corretas
chmod 755 debian/usr/lib/my-yt-down/my-yt-down
chmod -R 755 debian/usr/lib/my-yt-down/_internal
chmod 755 debian/usr/local/bin/my-yt-down

# Criar script de inicialização
cat > debian/usr/local/bin/my-yt-down << 'EOL'
#!/bin/bash
set -e

# Diretório base da aplicação
APP_DIR="/usr/lib/my-yt-down"
VENV_DIR="$APP_DIR/venv"

# Criar ambiente virtual se não existir
if [ ! -d "$VENV_DIR" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$APP_DIR/requirements.txt"
    deactivate
else
    # Verificar se as dependências estão instaladas no venv
    source "$VENV_DIR/bin/activate"
    if ! pip list | grep -q "yt-dlp"; then
        echo "Instalando dependências no ambiente virtual..."
        pip install --upgrade pip
        pip install -r "$APP_DIR/requirements.txt"
    fi
    deactivate
fi

# Verificar se o diretório de downloads existe e tem permissões corretas
if [ ! -d "$APP_DIR/downloads" ]; then
    sudo mkdir -p "$APP_DIR/downloads"
    sudo chmod 777 "$APP_DIR/downloads"
fi

# Verificar permissões do executável
if [ ! -x "$APP_DIR/my-yt-down" ]; then
    sudo chmod 755 "$APP_DIR/my-yt-down"
fi

# Ativar o ambiente virtual e executar o programa
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"
exec ./my-yt-down "$@"
EOL

chmod 755 debian/usr/local/bin/my-yt-down

# Criar arquivo .desktop
cat > debian/usr/share/applications/my-yt-down.desktop << EOL
[Desktop Entry]
Version=1.0
Name=YouTube Downloader
Comment=Download videos from YouTube
Exec=/usr/local/bin/my-yt-down
Icon=my-yt-down
Terminal=false
Type=Application
Categories=Utility;AudioVideo;
EOL

# Criar arquivo de controle
cat > debian/DEBIAN/control << 'EOF'
Package: my-yt-down
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.10), python3-tk, python3-pil, python3-pil.imagetk, python3-pip, python3-venv, ffmpeg, imagemagick
Maintainer: Your Name <your.email@example.com>
Description: YouTube Video Downloader
 A simple and efficient YouTube video downloader with GUI interface.
 Supports various video and audio formats with customizable quality options.
EOF

# Criar script postinst
cat > debian/DEBIAN/postinst << 'EOL'
#!/bin/bash
set -e

APP_DIR="/usr/lib/my-yt-down"
VENV_DIR="$APP_DIR/venv"

# Criar diretório de downloads com permissões corretas
mkdir -p "$APP_DIR/downloads"
chmod -R 777 "$APP_DIR/downloads"

# Criar e configurar ambiente virtual
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

# Corrigir permissões dos executáveis e diretórios
chmod 755 "$APP_DIR/my-yt-down"
chmod -R 755 "$APP_DIR/_internal"
chmod -R 755 "$VENV_DIR"
chmod 755 /usr/local/bin/my-yt-down

# Garantir que os diretórios tenham as permissões corretas
chmod 755 "$APP_DIR"
chmod 755 /usr/local/bin

# Corrigir propriedade dos arquivos
chown -R root:root "$APP_DIR"
chown -R root:root "$VENV_DIR"
chown root:root /usr/local/bin/my-yt-down

# Tornar o diretório de downloads gravável por todos os usuários
chmod 777 "$APP_DIR/downloads"
chown -R root:users "$APP_DIR/downloads"

# Atualizar cache de aplicativos
if [ -x "$(command -v update-desktop-database)" ]; then
    update-desktop-database
fi

exit 0
EOL

chmod 755 debian/DEBIAN/postinst

# Copiar requirements.txt para o pacote
cp requirements.txt debian/usr/lib/my-yt-down/

# Criar pacote
dpkg-deb --build debian my-yt-down.deb

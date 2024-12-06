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
    dpkg-dev

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

# Verificar outras dependências necessárias
DEPS=("python3-pip" "dpkg-dev" "ffmpeg")
for dep in "${DEPS[@]}"; do
    if ! dpkg -l | grep -q "^ii  $dep "; then
        echo "Instalando $dep..."
        apt-get install -y "$dep"
    fi
done

# Limpar diretórios anteriores
rm -rf build/ dist/ debian/

# Criar estrutura de diretórios
mkdir -p debian/DEBIAN
mkdir -p debian/usr/local/bin
mkdir -p debian/usr/lib/my-yt-down
mkdir -p debian/usr/share/applications
mkdir -p debian/usr/share/icons/hicolor/256x256/apps

# Criar ambiente virtual temporário
python3 -m venv build_venv
source build_venv/bin/activate

# Atualizar pip e instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Copiar biblioteca tkinter para o ambiente virtual
cp -r /usr/lib/python3*/tkinter build_venv/lib/python3*/ || true
cp -r /usr/lib/python3*/lib-dynload/_tkinter* build_venv/lib/python3*/lib-dynload/ || true

# Gerar executável com configurações específicas para Tkinter
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

# Copiar arquivos para a estrutura do pacote
cp -r dist/my-yt-down/* debian/usr/lib/my-yt-down/
cp src/assets/icon.png debian/usr/share/icons/hicolor/256x256/apps/my-yt-down.png

# Definir permissões corretas
chmod 755 debian/usr/lib/my-yt-down/my-yt-down
chmod -R 755 debian/usr/lib/my-yt-down/_internal
chmod 755 debian/usr/local/bin/my-yt-down

# Criar script de inicialização
cat > debian/usr/local/bin/my-yt-down << 'EOL'
#!/bin/bash
cd /usr/lib/my-yt-down
exec /usr/lib/my-yt-down/my-yt-down "$@"
EOL

# Garantir que o script de inicialização tenha as permissões corretas
chmod 755 debian/usr/local/bin/my-yt-down

# Criar arquivo .desktop
cat > debian/usr/share/applications/my-yt-down.desktop << EOL
[Desktop Entry]
Version=1.0
Name=YouTube Downloader
Comment=Download videos from YouTube
Exec=/usr/local/bin/my-yt-down
Icon=/usr/share/icons/hicolor/256x256/apps/my-yt-down.png
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
Depends: python3 (>= 3.10), python3-tk, python3-pil, python3-pil.imagetk, python3-pip, ffmpeg
Maintainer: Your Name <your.email@example.com>
Description: YouTube Video Downloader
 A simple and efficient YouTube video downloader with GUI interface.
 Supports various video and audio formats with customizable quality options.
EOF

# Criar script postinst
cat > debian/DEBIAN/postinst << 'EOL'
#!/bin/bash

# Criar diretório de downloads com permissões corretas
mkdir -p /usr/lib/my-yt-down/downloads
chmod 777 /usr/lib/my-yt-down/downloads

# Corrigir permissões dos executáveis
chmod 755 /usr/lib/my-yt-down/my-yt-down
chmod -R 755 /usr/lib/my-yt-down/_internal
chmod 755 /usr/local/bin/my-yt-down

exit 0
EOL

chmod 755 debian/DEBIAN/postinst

# Criar arquivo postrm
cat > debian/DEBIAN/postrm << 'EOF'
#!/bin/bash
update-desktop-database
EOF

chmod +x debian/DEBIAN/postrm

# Criar pacote
dpkg-deb --build debian my-yt-down.deb

# Limpar ambiente virtual temporário
deactivate
rm -rf build_venv

echo "Pacote .deb criado com sucesso!"
echo "Para instalar, use: sudo dpkg -i my-yt-down.deb"
echo "Se houver dependências faltando: sudo apt-get install -f"

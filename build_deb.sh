#!/bin/bash

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Verificar dependências necessárias
DEPS=("python3" "python3-dev" "python3-pip" "python3-venv" "dpkg-dev")
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

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Gerar executável
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
cp icon.png debian/usr/share/icons/hicolor/256x256/apps/my-yt-down.png

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

# Criar arquivo postinst
cat > debian/DEBIAN/postinst << 'EOF'
#!/bin/bash
chmod +x /usr/local/bin/my-yt-down
update-desktop-database
EOF

chmod +x debian/DEBIAN/postinst

# Criar arquivo postrm
cat > debian/DEBIAN/postrm << 'EOF'
#!/bin/bash
update-desktop-database
EOF

chmod +x debian/DEBIAN/postrm

# Definir permissões corretas
chown -R root:root debian/
find debian/ -type d -exec chmod 755 {} \;
find debian/ -type f -exec chmod 644 {} \;
chmod 755 debian/DEBIAN/postinst
chmod 755 debian/DEBIAN/postrm
chmod 755 debian/usr/local/bin/my-yt-down

# Criar pacote
dpkg-deb --build debian my-yt-down.deb

# Limpar ambiente virtual temporário
deactivate
rm -rf build_venv

echo "Pacote .deb criado com sucesso!"
echo "Para instalar, use: sudo dpkg -i my-yt-down.deb"
echo "Se houver dependências faltando: sudo apt-get install -f"

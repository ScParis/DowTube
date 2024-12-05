#!/bin/bash

# Ative o ambiente virtual
source venv/bin/activate

# Gere o executável com PyInstaller com opções adicionais
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

# Crie os diretórios necessários
mkdir -p debian/usr/lib/my-yt-down
mkdir -p debian/usr/share/applications
mkdir -p debian/usr/share/icons/hicolor/256x256/apps

# Copie o diretório dist completo
cp -r dist/my-yt-down/* debian/usr/lib/my-yt-down/

# Crie um script wrapper
mkdir -p debian/usr/local/bin
cat > debian/usr/local/bin/my-yt-down << 'EOF'
#!/bin/bash
cd /usr/lib/my-yt-down
./my-yt-down "$@"
EOF

# Torne o wrapper executável
chmod +x debian/usr/local/bin/my-yt-down

# Copie o ícone
cp debian/usr/share/icons/my-yt-down/my-yt-down.png debian/usr/share/icons/hicolor/256x256/apps/

# Atualize o arquivo .desktop
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

# Crie o pacote .deb
dpkg-deb --build debian my-yt-down.deb

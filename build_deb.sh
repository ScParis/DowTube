#!/bin/bash

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Adicionar repositório deadsnakes para Python 3.12
echo "Adicionando repositório para Python 3.12..."
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update

# Instalar Python 3.12 e dependências
echo "Instalando Python 3.12 e dependências..."
apt-get install -y python3.12 python3.12-dev python3.12-venv python3.12-distutils libpython3.12 libpython3.12-dev

# Verificar se Python 3.12 foi instalado corretamente
if ! command -v python3.12 &> /dev/null; then
    echo "Erro: Falha ao instalar Python 3.12"
    exit 1
fi

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

# Criar ambiente virtual temporário com Python 3.12
python3.12 -m venv build_venv
source build_venv/bin/activate

# Atualizar pip e instalar dependências
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
Depends: python3.12 (>= 3.12), python3-tk, python3-pip, ffmpeg, libpython3.12, python3-pil
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

# Criar pacote
dpkg-deb --build debian my-yt-down.deb

# Limpar ambiente virtual temporário
deactivate
rm -rf build_venv

echo "Pacote .deb criado com sucesso!"
echo "Para instalar, use: sudo dpkg -i my-yt-down.deb"
echo "Se houver dependências faltando: sudo apt-get install -f"

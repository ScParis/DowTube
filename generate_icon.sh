#!/bin/bash

# Instalar ImageMagick se necessário
if ! command -v convert &> /dev/null; then
    echo "Instalando ImageMagick..."
    sudo apt-get update
    sudo apt-get install -y imagemagick
fi

# Criar diretório de assets se não existir
mkdir -p src/assets

# Gerar ícone SVG
cat > src/assets/icon.svg << 'EOL'
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <circle cx="128" cy="128" r="120" fill="#FF0000"/>
  <polygon points="102,82 102,174 179,128" fill="white"/>
  <path d="M 179,128 L 102,174 L 102,82 L 179,128 Z" fill="white"/>
</svg>
EOL

# Converter SVG para PNG
convert src/assets/icon.svg -resize 256x256 src/assets/icon.png

echo "Ícone gerado com sucesso!"

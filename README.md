# YouTube Downloader

A modern, user-friendly YouTube media downloader with support for multiple formats and qualities.

## Features

- **Simple Interface**: Clean, intuitive GUI for easy downloads
- **Multiple Format Support**:
  - **Video Formats**:
    - MP4 (High/Medium/Low quality)
    - WebM (High/Medium/Low quality)
    - MKV (High/Medium/Low quality)
  - **Audio Formats**:
    - MP3 (High/Medium/Low quality)
    - AAC (High/Medium/Low quality)
    - Opus (High/Medium/Low quality)
- **Quality Options**:
  - Video:
    - High: Best available quality
    - Medium: 720p
    - Low: 480p
  - Audio:
    - High: Best bitrate (320kbps for MP3)
    - Medium: Medium bitrate (192kbps for MP3)
    - Low: Lower bitrate (128kbps for MP3)
- **Progress Tracking**: Real-time download progress monitoring
- **Custom Save Location**: Choose where to save your downloads
- **Error Handling**: Clear error messages and status updates

## Requirements

- Python 3.12 or higher
- FFmpeg (for audio extraction and format conversion)

## Installation

### Método Automático (Recomendado)

1. Clone o repositório:
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. Execute o script de instalação:
```bash
chmod +x install.sh
./install.sh
```

O script irá automaticamente:
- Criar e ativar um ambiente virtual
- Instalar todas as dependências Python
- Instalar o FFmpeg se necessário

### Método Manual

Se preferir instalar manualmente, siga estes passos:

1. Clone o repositório:
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
- **Linux**:
  ```bash
  sudo apt-get install ffmpeg  # Ubuntu/Debian
  sudo pacman -S ffmpeg       # Arch Linux
  ```
- **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- **macOS**:
  ```bash
  brew install ffmpeg
  ```

## Usage

1. Run the application:
```bash
python main.py
```

2. Enter a YouTube URL
3. Choose save location
4. Select format (Video/Audio)
5. Choose specific format (MP4/WebM/MKV or MP3/AAC/Opus)
6. Select quality (High/Medium/Low)
7. Click Download

## Project Structure

```
youtube-downloader/
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
├── src/
│   ├── gui.py       # GUI implementation
│   ├── downloader.py # Download handling
│   └── config.py    # Configuration management
└── downloads/       # Default download directory
```

## Dependencies

- customtkinter: Modern GUI framework
- yt-dlp: YouTube download functionality
- ffmpeg-python: Media processing
- Pillow: Image handling for GUI

## Configuration

- Default download location: `~/Downloads`
- Configuration file: `config.json`
- Supports custom save locations
- Format preferences are saved between sessions

## Error Handling

The application includes comprehensive error handling for:
- Invalid URLs
- Network issues
- Format conversion problems
- Disk space issues
- Permission errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# YouTube Downloader - User Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Graphical Interface

1. Start the application:
```bash
python src/gui.py
```

2. Enter a YouTube URL in the URL field

3. Select destination folder using the "Browse" button

4. Choose format:
   - MP3: For audio only
   - MP4: For video with audio

5. Select quality:
   - MP3:
     - High Quality (320K)
     - Medium Quality (192K)
     - Low Quality (128K)
   - MP4:
     - 1080p
     - 720p
     - 480p
     - 360p

6. Click "Start Download"

### Features

#### Preview
- Use the preview feature to check the content before downloading
- Preview length is limited to 30 seconds

#### Download History
- View recent downloads
- Check download status and details

#### Multiple Downloads
- Queue multiple downloads
- Cancel individual downloads
- Monitor progress of all downloads

## Configuration

The application can be configured by editing `src/config.py`:

- Download settings (chunk size, timeout)
- Cache settings
- Format options
- Interface preferences
- Performance limits

## Troubleshooting

### Common Issues

1. "URL Invalid":
   - Make sure the URL is from YouTube
   - URL should start with https://www.youtube.com/

2. "Insufficient Disk Space":
   - Free up disk space
   - Change download directory

3. "Download Failed":
   - Check internet connection
   - Try a different format/quality
   - Check if video is available in your region

### Logs

Logs are stored in the `logs` directory:
- `downloader.log`: Download operations
- Error details and debugging information

## Support

For issues and feature requests:
- Open an issue on GitHub
- Include log files when reporting problems
- Provide URL examples when relevant

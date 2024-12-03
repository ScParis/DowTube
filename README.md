# YouTube Downloader

A modern, feature-rich YouTube downloader with a beautiful graphical interface.

## Features

- 🎵 Download audio (MP3) and video (MP4)
- 🎨 Modern, user-friendly interface
- 📊 Multiple quality options
- 🔄 Parallel downloads
- 📥 Download queue management
- 🕒 Download history
- 🎯 Preview before download
- 📝 Detailed logging
- 🚀 Performance optimized
- 💾 Smart caching system

## Requirements

- Python 3.8+
- yt-dlp
- FFmpeg (for audio conversion)

## Quick Start

1. Clone the repository
2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/gui.py
```

## Documentation

- [User Guide](docs/USAGE.md)
- [API Documentation](docs/API.md)

## Project Structure

```
youtube-downloader/
├── src/                 # Source code
│   ├── __init__.py
│   ├── config.py       # Configuration
│   ├── downloader.py   # Core functionality
│   ├── gui.py         # User interface
│   └── utils.py       # Utilities
├── tests/              # Unit tests
├── docs/               # Documentation
├── downloads/          # Default download directory
├── logs/              # Log files
└── requirements.txt    # Dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- yt-dlp team for the excellent download engine
- CustomTkinter for the modern UI components
- All contributors and users

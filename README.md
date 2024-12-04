# DowTube

A modern, feature-rich YouTube downloader with a beautiful graphical interface built with CustomTkinter.

## Features

- 🎵 Download audio (MP3) and video (MP4)
- 🎨 Modern, dark-themed interface with CustomTkinter
- 📊 Multiple quality options for both audio and video
- 🔄 Parallel downloads with queue management
- 📑 Playlist download support
- ⭐ Favorites management
- 📅 Download scheduling
- ⚙️ Customizable settings
- 🎯 Media preview capabilities
- 📝 Detailed logging and error handling
- 🚀 Performance optimized
- 💾 Smart disk space management

## Requirements

- Python 3.10+
- FFmpeg (for media processing)
- System dependencies listed in requirements.txt

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DowTube.git
cd DowTube
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Documentation

- [User Guide](docs/USAGE.md)
- [Changelog](CHANGES.rst)

## Project Structure

```
DowTube/
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── downloader.py      # Download functionality
│   ├── gui.py            # User interface
│   └── utils.py          # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── downloads/            # Default download directory
├── logs/                 # Application logs
└── favorites/           # Saved favorites
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CustomTkinter for the modern UI framework
- yt-dlp for the robust download capabilities
- FFmpeg for media processing

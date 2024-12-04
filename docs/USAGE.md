# DowTube - User Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DowTube.git
cd DowTube
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

## Using DowTube

### Starting the Application

Launch DowTube by running:
```bash
python main.py
```

### Main Interface

The application features a modern, dark-themed interface with a sidebar navigation and multiple tabs:

#### Download Tab
1. Enter a YouTube URL in the input field
2. Choose download format:
   - Audio (MP3)
   - Video (MP4)
3. Select quality:
   - Audio Quality:
     - High (320K)
     - Medium (192K)
     - Low (128K)
   - Video Quality:
     - 1080p
     - 720p
     - 480p
     - 360p
4. Click "Download" to start

#### Playlist Tab
1. Enter a YouTube playlist URL
2. Select download options for all videos
3. Choose which videos to include
4. Start batch download

#### Favorites Tab
- Save frequently used URLs
- Organize your favorite videos
- Quick access to common downloads

#### Schedule Tab
- Schedule downloads for later
- Set up recurring downloads
- Manage scheduled tasks

#### Settings Tab
- Configure download directory
- Set default quality preferences
- Adjust application theme
- Manage system resources

### Additional Features

1. **Progress Tracking**
   - Real-time download progress
   - Speed and time remaining
   - Queue management

2. **Media Preview**
   - Thumbnail preview
   - Basic media information
   - Duration and quality info

3. **Error Handling**
   - Clear error messages
   - Automatic retry options
   - Detailed logging

4. **Disk Space Management**
   - Automatic space checking
   - Warning for insufficient space
   - Clean-up recommendations

## Troubleshooting

### Common Issues

1. **Download Fails**
   - Check internet connection
   - Verify URL is valid
   - Ensure sufficient disk space
   - Check logs for details

2. **Audio Conversion Issues**
   - Verify FFmpeg is installed
   - Check file permissions
   - Ensure temp directory is writable

3. **Interface Not Responding**
   - Check system resources
   - Reduce concurrent downloads
   - Restart application

### Getting Help

- Check the logs in the `logs` directory
- Review error messages in the application
- Submit issues on GitHub with log details

## Updates

DowTube checks for updates automatically. When available:
1. A notification will appear
2. Follow the update instructions
3. Restart the application

## Best Practices

1. **Optimal Performance**
   - Limit concurrent downloads
   - Regular cache cleanup
   - Monitor disk space

2. **Organization**
   - Use meaningful filenames
   - Organize downloads by category
   - Regularly backup favorites

3. **Resource Management**
   - Close unused tabs
   - Clear download history
   - Remove completed downloads

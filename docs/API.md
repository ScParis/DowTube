# API Documentation

## MediaDownloader

The main class responsible for downloading media from YouTube.

### Methods

#### `get_media_info(url: str) -> Dict`
Retrieves information about a video or playlist.

**Parameters:**
- `url`: YouTube URL

**Returns:**
- Dictionary containing video information

#### `download_media(url: str, output_dir: Path, format_info: Dict, callback: Optional[Callable] = None) -> None`
Starts a media download.

**Parameters:**
- `url`: YouTube URL
- `output_dir`: Directory to save the downloaded file
- `format_info`: Dictionary containing format and quality information
- `callback`: Optional callback function for progress updates

#### `preview_media(url: str, format_info: Dict, callback: Optional[Callable] = None) -> Path`
Generates a preview of the video/audio.

**Parameters:**
- `url`: YouTube URL
- `format_info`: Dictionary containing format and quality information
- `callback`: Optional callback function for progress updates

**Returns:**
- Path to the preview file

#### `cancel_download(download_id: int)`
Cancels an active download.

**Parameters:**
- `download_id`: ID of the download to cancel

#### `get_active_downloads() -> List[Dict]`
Returns information about active downloads.

**Returns:**
- List of dictionaries containing download information

## Utils

### URL Validation

#### `validate_url(url: str) -> bool`
Validates a YouTube URL.

**Parameters:**
- `url`: URL to validate

**Returns:**
- `True` if valid, raises `ValidationError` if invalid

### File System

#### `check_disk_space(path: Union[str, Path]) -> bool`
Checks if there's enough disk space.

**Parameters:**
- `path`: Path to check

**Returns:**
- `True` if enough space, raises `ValidationError` if not

#### `sanitize_filename(filename: str) -> str`
Removes invalid characters from filename.

**Parameters:**
- `filename`: Original filename

**Returns:**
- Sanitized filename

### Formatting

#### `format_size(size_bytes: int) -> str`
Formats size in bytes to human-readable format.

**Parameters:**
- `size_bytes`: Size in bytes

**Returns:**
- Formatted string (e.g., "1.5 MB")

#### `format_duration(seconds: int) -> str`
Formats duration in seconds to human-readable format.

**Parameters:**
- `seconds`: Duration in seconds

**Returns:**
- Formatted string (e.g., "1h 30m")

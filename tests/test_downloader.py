import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.downloader import MediaDownloader, DownloadError, DownloadTask

class TestMediaDownloader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = MediaDownloader()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        self.downloader.cleanup()

    @patch('subprocess.run')
    def test_get_media_info(self, mock_run):
        # Simula resposta do yt-dlp
        mock_run.return_value.stdout = '{"title": "Test Video", "duration": 100}'
        mock_run.return_value.returncode = 0

        info = self.downloader.get_media_info("https://www.youtube.com/watch?v=test")
        self.assertEqual(info["title"], "Test Video")
        self.assertEqual(info["duration"], 100)

    @patch('subprocess.Popen')
    def test_download_media(self, mock_popen):
        # Simula processo de download
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Simula callback
        callback = MagicMock()

        # Tenta download
        self.downloader.download_media(
            "https://www.youtube.com/watch?v=test",
            Path(self.temp_dir),
            {"format": "mp3", "quality": "320K"},
            callback
        )

        # Verifica se o download foi iniciado
        self.assertTrue(mock_popen.called)

    def test_invalid_url(self):
        with self.assertRaises(DownloadError):
            self.downloader.download_media(
                "invalid_url",
                Path(self.temp_dir),
                {"format": "mp3", "quality": "320K"}
            )

    @patch('subprocess.Popen')
    def test_cancel_download(self, mock_popen):
        # Simula processo de download
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        # Inicia download
        task = DownloadTask(
            url="https://www.youtube.com/watch?v=test",
            output_path=Path(self.temp_dir) / "test.mp3",
            format_info={"format": "mp3", "quality": "320K"}
        )
        
        download_id = id(task)
        self.downloader.download_queue.put(task)
        
        # Cancela download
        self.downloader.cancel_download(download_id)
        
        # Verifica se o processo foi terminado
        self.assertTrue(mock_process.terminate.called)

    def test_preview_media(self):
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = 0
            mock_popen.return_value = mock_process

            preview_path = self.downloader.preview_media(
                "https://www.youtube.com/watch?v=test",
                {"format": "mp3", "quality": "320K"}
            )

            self.assertTrue(mock_popen.called)
            self.assertTrue("preview" in str(preview_path))

if __name__ == '__main__':
    unittest.main()

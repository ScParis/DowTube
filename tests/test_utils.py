import unittest
import tempfile
import shutil
from pathlib import Path
from src.utils import (
    validate_url, check_disk_space, sanitize_filename,
    format_size, format_duration, ValidationError
)

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_validate_url_valid(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLxxx"
        ]
        for url in valid_urls:
            self.assertTrue(validate_url(url))

    def test_validate_url_invalid(self):
        invalid_urls = [
            "",
            "not a url",
            "https://example.com",
            "https://youtube.com/invalid"
        ]
        for url in invalid_urls:
            with self.assertRaises(ValidationError):
                validate_url(url)

    def test_check_disk_space(self):
        # Assumindo que o diretório temporário tem espaço suficiente
        self.assertTrue(check_disk_space(self.temp_dir))

    def test_sanitize_filename(self):
        test_cases = [
            ("hello/world", "hello_world"),
            ('file:with:colons', "file_with_colons"),
            ('file"with"quotes', "file_with_quotes"),
            ("a" * 300, "a" * 255)  # Testa limite de tamanho
        ]
        for input_name, expected in test_cases:
            self.assertEqual(sanitize_filename(input_name), expected)

    def test_format_size(self):
        test_cases = [
            (500, "500.00 B"),
            (1024, "1.00 KB"),
            (1024 * 1024, "1.00 MB"),
            (1024 * 1024 * 1024, "1.00 GB")
        ]
        for input_size, expected in test_cases:
            self.assertEqual(format_size(input_size), expected)

    def test_format_duration(self):
        test_cases = [
            (30, "30s"),
            (90, "1m 30s"),
            (3600, "1h 0m 0s"),
            (3661, "1h 1m 1s")
        ]
        for input_duration, expected in test_cases:
            self.assertEqual(format_duration(input_duration), expected)

if __name__ == '__main__':
    unittest.main()

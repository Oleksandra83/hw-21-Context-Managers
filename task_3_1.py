import logging
import pytest

logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomFile:

    def __init__(self, filename, mode='r', encoding='utf-8', suppress_exceptions=False):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.file = None
        self.suppress_exceptions = suppress_exceptions
        self.lines_processed = 0
        self.logger = logging.getLogger(f'CustomFile-{filename}')

    def __enter__(self):
        self.logger.info(f"Відкриваємо '{self.filename}' у режимі '{self.mode}'.")
        self.file = open(self.filename, self.mode, encoding=self.encoding)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.file:
            self.file.close()
        return self.suppress_exceptions and exc_type is not None

    def write(self, text):
        self.file.write(text)
        self.lines_processed += len(text.splitlines())

    def read(self, *args, **kwargs):
        content = self.file.read(*args, **kwargs)
        self.lines_processed = len(content.splitlines())
        return content

    def readline(self, *args, **kwargs):
        line = self.file.readline(*args, **kwargs)
        if line:
            self.lines_processed += 1
        return line

    def readlines(self, *args, **kwargs):
        lines = self.file.readlines(*args, **kwargs)
        self.lines_processed = len(lines)
        return lines

    def __getattr__(self, name):
        """Делегування інших методів до реального файлу."""
        return getattr(self.file, name)

# -------- Функція для аналізу --------
def analyze_file(file_obj):
    content = file_obj.read().strip()
    if not content:
        return {"word_count": 0, "line_count": 0, "unique_word_count": 0}

    lines = content.split("\n")
    words = content.split()
    unique_words = set(words)

    return {
        "word_count": len(words),
        "line_count": len(lines),
        "unique_word_count": len(unique_words)
    }

@pytest.fixture
def custom_file_fixture(tmp_path):
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("Рядок один\nРядок два\nРядок один", encoding="utf-8")

    with CustomFile(str(temp_file), "r", encoding="utf-8") as cf:
        yield cf

# -------- Тест --------
def test_analyze_file_with_fixture(custom_file_fixture):
    results = analyze_file(custom_file_fixture)

    assert results["word_count"] == 6
    assert results["line_count"] == 3
    assert results["unique_word_count"] == 3  # 'Рядок', 'один', 'два'

    assert custom_file_fixture.lines_processed == 3
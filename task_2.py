import logging
import os
import unittest
import io
from task_1 import CustomFile  # Імпортуємо клас з твого основного файлу

# Вимикаємо інформаційне логування під час тестів
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')


class TestCustomFile(unittest.TestCase):
    """Тестовий клас для CustomFile."""

    def setUp(self):
        """Створюємо тестовий файл перед кожним тестом."""
        self.test_filename = "test_file.tmp"
        with open(self.test_filename, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

    def tearDown(self):
        """Видаляємо тестовий файл після кожного тесту."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    # --- Позитивні тести ---

    def test_write_and_read(self):
        """Перевіряємо запис та читання файлу."""
        content_to_write = "New content\nAnother line"
        with CustomFile(self.test_filename, 'w') as cf:
            cf.write(content_to_write)
            self.assertEqual(cf.lines_processed, 2)

        with CustomFile(self.test_filename, 'r') as cf:
            read_content = cf.read()
            self.assertEqual(read_content, content_to_write)
            self.assertEqual(cf.lines_processed, 2)

    def test_multiple_writes_line_count(self):
        """Перевіряємо, що лічильник коректно рахує кілька записів."""
        with CustomFile(self.test_filename, 'w') as cf:
            cf.write("Line A\n")
            cf.write("Line B\nLine C\n")
            self.assertEqual(cf.lines_processed, 3)

    def test_readline(self):
        """Перевіряємо читання по рядках та лічильник."""
        expected_lines = ["Line 1\n", "Line 2\n", "Line 3\n"]
        with CustomFile(self.test_filename, 'r') as cf:
            for i, expected_line in enumerate(expected_lines):
                actual_line = cf.readline()
                self.assertEqual(actual_line, expected_line)
                self.assertEqual(cf.lines_processed, i + 1)
            self.assertEqual(cf.readline(), "")  # Кінець файлу

    def test_readlines(self):
        """Перевіряємо читання всіх рядків та лічильник."""
        with CustomFile(self.test_filename, 'r') as cf:
            lines = cf.readlines()
            self.assertEqual(len(lines), 3)
            self.assertEqual(cf.lines_processed, 3)
            self.assertEqual(lines[0], "Line 1\n")
            self.assertEqual(lines[2], "Line 3\n")

    def test_append_mode(self):
        """Перевіряємо режим дописування."""
        with CustomFile(self.test_filename, 'a') as cf:
            cf.write("Line 4\n")
            self.assertEqual(cf.lines_processed, 1)

        with open(self.test_filename, 'r') as f:
            content = f.read()
            self.assertEqual(content, "Line 1\nLine 2\nLine 3\nLine 4\n")

    def test_delegated_methods(self):
        """Перевіряємо, чи працює делегування методів."""
        with CustomFile(self.test_filename, 'r') as cf:
            cf.readline()
            pos = cf.tell()
            self.assertGreater(pos, 0)

            cf.seek(0)
            self.assertEqual(cf.tell(), 0)

    # --- Негативні тести (винятки) ---

    def test_file_not_found_error(self):
        """Перевіряємо, чи виникає FileNotFoundError для неіснуючого файлу."""
        with self.assertRaises(FileNotFoundError):
            with CustomFile("nonexistent_file.txt", 'r'):
                pass

    def test_exception_not_suppressed(self):
        """Перевіряємо, що виняток поширюється за замовчуванням."""
        with self.assertRaises(ValueError):
            with CustomFile(self.test_filename, 'r') as cf:
                raise ValueError("This exception should be raised.")

    def test_exception_suppressed(self):
        """Перевіряємо, що виняток пригнічується."""
        # Якщо виняток пригнічується, код після with виконається
        with CustomFile(self.test_filename, 'r', suppress_exceptions=True):
            raise ValueError("Suppressed error")

    def test_write_in_read_mode(self):
        """Перевіряємо, чи не можна писати у файл, відкритий у режимі читання."""
        with self.assertRaises(io.UnsupportedOperation):
            with CustomFile(self.test_filename, 'r') as cf:
                cf.write("This should fail.")

    def test_close_error_handling(self):
        """Перевіряємо, що помилки при закритті не ламають контекстний менеджер."""

        class BadCloseFile(CustomFile):
            def __exit__(self, exc_type, exc_value, exc_tb):
                if self.file:
                    def bad_close():
                        raise OSError("Close error")

                    self.file.close = bad_close
                return super().__exit__(exc_type, exc_value, exc_tb)

        with BadCloseFile(self.test_filename, 'r') as cf:
            cf.read()


if __name__ == '__main__':
    unittest.main()
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomFile:
    """
    Контекстний менеджер, що імітує функцію open(),
    додає лічильник оброблених рядків і логування.
    """
    def __init__(self, filename, mode='r', encoding='utf-8', suppress_exceptions=False):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.file = None
        self.suppress_exceptions = suppress_exceptions
        self.lines_processed = 0
        self.logger = logging.getLogger(f'CustomFile-{filename}')

    def __enter__(self):
        self.logger.info(f"Вхід у контекст: відкриваємо '{self.filename}' у режимі '{self.mode}'.")
        try:
            self.file = open(self.filename, self.mode, encoding=self.encoding)
        except FileNotFoundError as e:
            self.logger.error(f"Файл '{self.filename}' не знайдено.")
            raise
        return self  # Повертаємо self, щоб можна було доступитися до лічильника

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            if self.file:
                self.logger.info(f"Закриваємо файл '{self.filename}'.")
                self.file.close()
        except Exception as close_err:
            self.logger.error(f"Помилка при закритті файлу: {close_err}")

        if exc_type:
            self.logger.error(f"Виняток '{exc_type.__name__}' у блоці with: {exc_value}")
            self.logger.info(f"Кількість оброблених рядків: {self.lines_processed}")
            if self.suppress_exceptions:
                self.logger.info("Виняток пригнічено.")
                return True
            else:
                self.logger.info("Виняток буде поширено.")
                return False

        self.logger.info(f"Блок with завершено без винятків. Оброблено рядків: {self.lines_processed}")
        return False

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
        """Делегування інших методів до реального об'єкта файлу."""
        return getattr(self.file, name)

with CustomFile('example.txt', 'w') as f:
    f.write("Рядок 1\nРядок 2\n")
    f.write("Ще один рядок")

with CustomFile('example.txt', 'r') as f:
    data = f.read()
    print("Прочитано:", data)
    print("Рядків оброблено:", f.lines_processed)
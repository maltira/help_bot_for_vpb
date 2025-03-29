import logging
import os

log_file = "help_bot/logs/bot.log"

# Настройка логгера
logging.basicConfig(
    filename=log_file,  # Путь к файлу логов
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"  # Указываем кодировку UTF-8,
)
logging.getLogger("aiogram").setLevel(logging.WARNING)  # Показывать только предупреждения и ошибки
logger = logging.getLogger(__name__)

def clean_logs(max_lines):
    # Очищает лог, если строк больше max_lines
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) > max_lines:
            print(len(lines))
            with open(log_file, "w", encoding="utf-8") as f:
                f.writelines(lines[-max_lines:])  # Оставляем последние max_lines строк
            logger.info('Логи бота очищены')
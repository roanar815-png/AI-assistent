"""
Централизованная конфигурация логирования для всего приложения
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


# Создаем директорию для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Формат логов
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Цветной вывод для консоли
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[35m',   # Magenta
    'RESET': '\033[0m'        # Reset
}


class ColoredFormatter(logging.Formatter):
    """Форматтер с цветным выводом для консоли"""
    
    def format(self, record):
        # Добавляем цвет к уровню логирования
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Создает и настраивает логгер с единой конфигурацией
    
    Args:
        name: Имя логгера (обычно __name__ модуля)
        level: Уровень логирования (по умолчанию INFO)
    
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    
    # Если логгер уже настроен, возвращаем его
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    logger.propagate = False
    
    # === Консольный обработчик (с цветами) ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # === Файловый обработчик - общий лог ===
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(
        LOG_DIR / f"app_{today}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # === Файловый обработчик - только ошибки ===
    error_handler = logging.FileHandler(
        LOG_DIR / f"errors_{today}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер с настроенной конфигурацией
    
    Args:
        name: Имя логгера (обычно __name__ модуля)
    
    Returns:
        Настроенный логгер
    """
    return setup_logger(name)


# Функции для быстрого логирования
def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """Логирование вызова функции с параметрами"""
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"🔄 Вызов функции: {func_name}({params})")


def log_success(logger: logging.Logger, message: str, **details):
    """Логирование успешной операции"""
    if details:
        details_str = " | ".join([f"{k}={v}" for k, v in details.items()])
        logger.info(f"✅ {message} | {details_str}")
    else:
        logger.info(f"✅ {message}")


def log_error(logger: logging.Logger, message: str, error: Exception = None, **details):
    """Логирование ошибки"""
    if details:
        details_str = " | ".join([f"{k}={v}" for k, v in details.items()])
        error_msg = f"❌ {message} | {details_str}"
    else:
        error_msg = f"❌ {message}"
    
    if error:
        logger.error(f"{error_msg} | Exception: {str(error)}", exc_info=True)
    else:
        logger.error(error_msg)


def log_warning(logger: logging.Logger, message: str, **details):
    """Логирование предупреждения"""
    if details:
        details_str = " | ".join([f"{k}={v}" for k, v in details.items()])
        logger.warning(f"⚠️ {message} | {details_str}")
    else:
        logger.warning(f"⚠️ {message}")


# Главный логгер приложения
app_logger = get_logger("AIAI_APP")


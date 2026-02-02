import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging():
    logger = logging.getLogger("ip_blacklist")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Log general
    app_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    # Log de errores
    error_handler = RotatingFileHandler(
        LOG_DIR / "error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Evitar duplicados
    if not logger.handlers:
        logger.addHandler(app_handler)
        logger.addHandler(error_handler)

    return logger

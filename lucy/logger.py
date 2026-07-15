import os
import logging
from logging.handlers import TimedRotatingFileHandler
from colorama import Fore, Style, init as colorama_init

from lucy.context import request_id_var

try:
    from lucy.config import LOGGING_DIR, LOGGING_LIMIT_DAYS, LOG_TO_CONSOLE
except Exception:
    LOGGING_DIR = "logs/"
    LOGGING_LIMIT_DAYS = 1
    LOG_TO_CONSOLE = False

colorama_init(autoreset=True)

os.makedirs(LOGGING_DIR, exist_ok=True)
LOG_FILENAME = os.path.join(LOGGING_DIR, "app.log")

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "req_id=%(request_id)s | %(message)s"
)

COLOR_FORMATS = {
    "DEBUG":    Fore.CYAN + LOG_FORMAT + Style.RESET_ALL,
    "INFO":     Fore.WHITE + LOG_FORMAT + Style.RESET_ALL,
    "WARNING":  Fore.YELLOW + LOG_FORMAT + Style.RESET_ALL,
    "ERROR":    Fore.RED + LOG_FORMAT + Style.RESET_ALL,
    "CRITICAL": Fore.RED + Style.BRIGHT + LOG_FORMAT + Style.RESET_ALL,
}


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        fmt = COLOR_FORMATS.get(record.levelname, LOG_FORMAT)
        return logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S").format(record)


def get_logger(name: str = "app", level = logging.INFO, console: bool = LOG_TO_CONSOLE) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        request_filter = RequestIdFilter()

        # Console
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.addFilter(request_filter)
            ch.setFormatter(ColoredFormatter())
            logger.addHandler(ch)

        # File
        fh = TimedRotatingFileHandler(
            LOG_FILENAME,
            when="midnight",
            interval=1,
            backupCount=LOGGING_LIMIT_DAYS,
            encoding="utf-8",
            utc=False,
        )

        fh.setLevel(level)
        fh.addFilter(request_filter)
        fh.setFormatter(
            logging.Formatter(
                LOG_FORMAT,
                "%Y-%m-%d %H:%M:%S",
            )
        )

        fh.suffix = "%Y-%m-%d"

        def namer(default_name: str) -> str:
            base_with_ext, date = default_name.rsplit(".", 1)
            root, ext = os.path.splitext(base_with_ext)
            return f"{root}.{date}{ext}"

        fh.namer = namer

        logger.addHandler(fh)

    return logger
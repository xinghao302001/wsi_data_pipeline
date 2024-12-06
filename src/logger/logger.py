import logging
import logging.config
import os


class LoggingSetup:
    """
    A class to configure logging with console and file handlers.
    """

    def __init__(
        self,
        log_file: str = "data_pipeline.log",
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        date_format: str = "%Y-%m-%d %H:%M:%S",
        max_file_size: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,  # Number of backup files to keep
    ):
        """
        Initialize the LoggingSetup class with default or custom configurations.

        :param log_file: Path to the log file.
        :param log_level: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :param log_format: Format for log messages.
        :param date_format: Date format for log messages.
        :param max_file_size: Maximum size of a single log file in bytes.
        :param backup_count: Number of backup log files to keep.
        """
        self.log_file = log_file
        self.log_level = log_level
        self.log_format = log_format
        self.date_format = date_format
        self.max_file_size = max_file_size
        self.backup_count = backup_count

    def setup(self):
        """
        Sets up the logging configuration using the provided parameters.
        """
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.log_format,
                    "datefmt": self.date_format,
                },
                "simple": {
                    "format": "%(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.log_level,
                    "formatter": "default",
                    "filename": self.log_file,
                    "maxBytes": self.max_file_size,
                    "backupCount": self.backup_count,
                    "encoding": "utf8",
                },
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console", "file"],
            },
        }

        logging.config.dictConfig(logging_config)
        logging.info(
            "Logging has been configured. Logs will be written to '%s'.", self.log_file
        )

"""
Logger Module
Handles logging and error tracking
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """Custom logger for Git client"""

    def __init__(self, log_dir: Optional[str] = None, verbose: bool = False):
        """
        Initialize Logger

        Args:
            log_dir: Custom log directory path
            verbose: Enable verbose logging
        """
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.home() / ".gitc" / "logs"

        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp
        log_file = self.log_dir / f"gitc_{datetime.now().strftime('%Y%m%d')}.log"

        # Configure logging
        self.logger = logging.getLogger('gitc')
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler (only for errors)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        if verbose:
            self.logger.addHandler(console_handler)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)


class GitClientException(Exception):
    """Base exception for Git client"""
    pass


class SSHKeyException(GitClientException):
    """Exception for SSH key operations"""
    pass


class GitOperationException(GitClientException):
    """Exception for Git operations"""
    pass


class ConfigException(GitClientException):
    """Exception for configuration operations"""
    pass


class BranchException(GitClientException):
    """Exception for branch operations"""
    pass

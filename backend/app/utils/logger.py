import logging
import sys
from datetime import datetime
from typing import Optional

# ANSI color codes
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Emojis for each log level
EMOJIS = {
    'INFO': 'ℹ️',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WARNING': '⚠️',
    'DEBUG': '🐛'
}

# Colors for each log level
LEVEL_COLORS = {
    'INFO': Colors.BLUE,
    'SUCCESS': Colors.GREEN,
    'ERROR': Colors.RED,
    'WARNING': Colors.YELLOW,
    'DEBUG': Colors.GRAY
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis."""
    
    def format(self, record):
        # Get timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get level name
        level = record.levelname
        if hasattr(record, 'custom_level'):
            level = record.custom_level
        
        # Get emoji and color
        emoji = EMOJIS.get(level, '')
        color = LEVEL_COLORS.get(level, Colors.RESET)
        
        # Get component name
        component = record.name if record.name != 'root' else 'APP'
        
        # Format message
        message = record.getMessage()
        
        # Build formatted log
        log_line = f"[{timestamp}] {emoji} {color}{Colors.BOLD}[{level}]{Colors.RESET} {color}[{component}]{Colors.RESET} - {message}"
        
        # Add exception info if present
        if record.exc_info:
            log_line += '\n' + self.formatException(record.exc_info)
        
        return log_line


class StudyBuddyLogger:
    """Custom logger for StudyBuddy application."""
    
    def __init__(self, component: str = "APP"):
        self.component = component
        self.logger = logging.getLogger(component)
        
        # Set level to DEBUG to capture all logs
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Set custom formatter
        formatter = ColoredFormatter()
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def info(self, message: str):
        """Log info message."""
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0, message, (), None
        )
        record.custom_level = 'INFO'
        self.logger.handle(record)
    
    def success(self, message: str):
        """Log success message."""
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0, message, (), None
        )
        record.custom_level = 'SUCCESS'
        self.logger.handle(record)
    
    def error(self, message: str, exc_info: Optional[Exception] = None):
        """Log error message."""
        record = self.logger.makeRecord(
            self.logger.name, logging.ERROR, "", 0, message, (), 
            (type(exc_info), exc_info, exc_info.__traceback__) if exc_info else None
        )
        record.custom_level = 'ERROR'
        self.logger.handle(record)
    
    def warning(self, message: str):
        """Log warning message."""
        record = self.logger.makeRecord(
            self.logger.name, logging.WARNING, "", 0, message, (), None
        )
        record.custom_level = 'WARNING'
        self.logger.handle(record)
    
    def debug(self, message: str):
        """Log debug message."""
        record = self.logger.makeRecord(
            self.logger.name, logging.DEBUG, "", 0, message, (), None
        )
        record.custom_level = 'DEBUG'
        self.logger.handle(record)


# Global logger instances for different components
_loggers = {}

def get_logger(component: str = "APP") -> StudyBuddyLogger:
    """Get or create a logger for a specific component."""
    if component not in _loggers:
        _loggers[component] = StudyBuddyLogger(component)
    return _loggers[component]

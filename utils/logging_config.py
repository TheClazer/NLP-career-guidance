import logging
import sys
from pathlib import Path
from config import settings

def setup_logging(name: str = "career_nlp") -> logging.Logger:
    """
    Configures and returns a logger with the specified name.
    Ensures logs are written to both stdout and a file.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        log_file = settings.LOG_DIR / "app.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file logging fails (e.g. permission issues)
        sys.stderr.write(f"Failed to setup file logging: {e}\n")

    return logger

# Create a default logger instance
logger = setup_logging()

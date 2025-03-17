import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(app):
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Set up file handler for all logs
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )

    # Set up formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # Set up specific loggers for different components
    loggers = {
        'face_detection': logging.INFO,
        'file_storage': logging.INFO,
        'rate_limiter': logging.INFO,
        'error_handler': logging.ERROR
    }

    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.addHandler(file_handler)

    # Log application startup
    app.logger.info(f"Application started in {app.config['ENV']} mode")
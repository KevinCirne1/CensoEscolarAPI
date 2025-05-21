import logging
import os
from datetime import datetime

def setup_logging():
    """Configura o logging para a aplicação."""
    
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    
    log_file = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"

    
    logger = logging.getLogger("censo_escolar_api")
    logger.setLevel(logging.INFO)

    
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger
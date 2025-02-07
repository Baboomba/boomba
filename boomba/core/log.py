from datetime import datetime
import logging
from typing import Dict, Any

from boomba.core.config import Conf
from boomba.core.constants import LOG_DIR, LOG_CONFIG



class Logger:
    _logger: logging.Logger
    log_conf: Dict[str, Any] = LOG_CONFIG
    
    def __init__(self, directory: str='system') -> None:
        self._directory = directory
        self._logger = self._configure_logger()

    def _set_file_path(self) -> None:
        file_name = f"{datetime.now().strftime('%Y%m%d')}"
        file_path = LOG_DIR / self._directory / file_name
            
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_conf['handlers']['file']['filename'] = str(file_path)
    
    def _remove_console_handler(self) -> None:
        self.log_conf['root']['handlers'].remove('console')
        
    def _configure_logger(self) -> logging.Logger:
        self._set_file_path()
        if not Conf.debug_mode:
            self._remove_console_handler()
        logging.config.dictConfig(self.log_conf)
        return logging.getLogger()
        
    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def debug(self, msg: str) -> None:
        self._logger.debug(msg)
    
    def info(self, msg: str) -> None:
        self._logger.info(msg)
        
    def warning(self, msg: str) -> None:
        self._logger.warning(msg)
    
    def error(self, msg: str) -> None:
        self._logger.error(msg)
    
    def critical(self, msg: str) -> None:
        self._logger.critical(msg)
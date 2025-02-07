from pathlib import Path
from typing import Dict, Any

PYTHON_VERSION = '3.13.1'
BOOMBA_VERSION = '0.1.0b1'

# The pakage directory
BOOMBA_DIR: Path = Path(__file__).resolve().parent.parent

# template directory
TPL_DIR = BOOMBA_DIR / 'template'


# The project directory of users
BASE_DIR: Path = Path.cwd()

# The directory and path of 'setting.py'
CONF_DIR = BASE_DIR / 'config'
CONF_PATH = BASE_DIR / CONF_DIR / 'settings.py'

# The directory of pipeline
PIPELINE_DIR  = BASE_DIR / 'pipeline'

# The default directory of data. it can be changed by users.
DATA_DIR = BASE_DIR / 'data'

# The directory of log
LOG_DIR = BASE_DIR / 'log'

# The time interval of run-loop. The unit is second.
LOOP_INTERVAL: int = 1

# The mode for writing the log file.
LOG_MODE: str = 'a'

# The encoding rule for writing
ENCODING: str = 'utf-8'

# The base file format for loading
BASE_DATA_FORMAT: str = 'parquet'

# The base date format for the attributes, start_date, and end_date of Loader class
DATE_FORMAT: str = 'YYYYMMDD'

# for APIExtractor
ACCEPT_HEADERS: Dict[str, str] = {
    "Accept": "application/json"
}

# for APIExtractor
CONTENT_HEADERS: Dict[str, str] = {
    "Content-Type": "application/json"
}

# To prevent errors when creating the Config() object during the first command execution
MOCK_CONFIG: Dict[str, Any] = {
    'database': {
        'mock_db': {
            'drivername': 'sqlite',
            'database': 'db',
        }
    },
    'base_db': 'mock_db',
}

LOG_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'standard',
            'filename': ''
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}
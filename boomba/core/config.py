from typing import Dict, Any
from pathlib import Path
from boomba.core.constants import CONF_PATH, MOCK_CONFIG


class Config:
    is_mock: bool
    conf_path: Path
    
    def __init__(self, conf_path: Path=None) -> None:
        self.is_mock = False
        self.conf_path = conf_path or Path(CONF_PATH)
        self._vars = self._load()
        self._set_attr()
    
    def __repr__(self) -> str:
        return (
            f"Config(var={self._vars}, is_mock={self.is_mock})"
        )
    
    def _load(self) -> Dict[str, Any]:
        if not self.conf_path.exists():
            return self._temp_config()
        
        with open(str(self.conf_path)) as f:
                conf = f.read()
        
        vars = {}
        exec(conf, {}, vars)
        return vars
    
    def _temp_config(self) -> Dict[str, Any]:
        self.is_mock = True
        return MOCK_CONFIG
    
    def _set_attr(self) -> None:
        for k, v in self._vars.items():
            if not k.startswith('__'):
                setattr(self, k.lower(), v)


Conf = Config()
from typing import Dict, Any
from pathlib import Path
import warnings
from boomba.core.constants import CONF_PATH, MOCK_CONFIG
            

class Config:
    is_mock: bool = False
    
    def __init__(self) -> None:
        self._vars = self._load()
        self._set_attr()
        
    def __repr__(self) -> str:
        return (
            f"Config(var={self._vars}, is_mock={self._mock})"
        )
    
    def _load(self) -> Dict[str, Any]:
        if not Path(CONF_PATH).exists():
            warnings.warn(
                "There is no 'settings.py'. It is substituted "
                "by a temporary configuration"
            )
            return self._temp_config()
                
        with open(CONF_PATH) as f:
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
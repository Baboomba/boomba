from string import Template
from typing import Dict
from pathlib import Path

from boomba.core.constants import (
                            DATA_DIR,
                            LOG_DIR,
                            CONF_DIR,
                            PIPELINE_DIR,
                            TPL_DIR
                        )


class Generator:
    directories: Dict[str, Path] = {
        'data': DATA_DIR,
        'log': LOG_DIR,
        'conf': CONF_DIR
    }
    
    conf_path: Dict[str, Path] = {
        'settings': TPL_DIR / 'settings.py-tpl'
    }
    
    pipe_dir: Path = TPL_DIR / 'pipeline'
    pipe_path: Dict[str, str] = {
        'extraction': pipe_dir / 'extraction.py-tpl',
        'load': pipe_dir / 'load.py-tpl',
        'schedule': pipe_dir / 'schedule.py-tpl',
        'schema': pipe_dir / 'schema.py-tpl',
        'transformation': pipe_dir / 'transformation.py-tpl',
    }
    
    def convert_template(
        self,
        file_path: str,
        output_path: str,
        context: Dict[str, str]=None
    ) -> None:
        with open(file_path, 'r') as tpl_file:
            tpl_file = tpl_file.read()
        
        if context is None:
            context = {}
            
        template = Template(tpl_file)
        output = template.substitute(context)

        with open(output_path, "w") as file:
            file.write(output)
            
    def init_directories(self) -> None:
        for _, dir in self.directories.items():
            Path(dir).mkdir(parents=True, exist_ok=False)
        
        for k, v in self.conf_path.items():
            self.convert_template(
                file_path=v,
                output_path=CONF_DIR / f"{k}.py"
            )
        
    def create_pipeline(self, pipe_name: str) -> None:
        dir = PIPELINE_DIR / pipe_name
        try:
            dir.mkdir(parents=True, exist_ok=False)
        except Exception as e:
            raise FileExistsError(f"'{pipe_name}' already exists.") from e
        for k, v in self.pipe_path.items():
            self.convert_template(
                file_path=v,
                output_path=dir / f"{k}.py"
            )
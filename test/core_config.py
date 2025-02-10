import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from unittest.mock import patch, MagicMock

from tempfile import NamedTemporaryFile
from boomba.core.config import Config
from boomba.core.constants import MOCK_CONFIG


class TestConfigFileReader(unittest.TestCase):
    
    def test_load_non_empty(self):
        content = 'FIRST_VAR="first_value"; SECOND_VAR="second_value"'
        return_value = {'FIRST_VAR': 'first_value', 'SECOND_VAR': 'second_value'}

        with NamedTemporaryFile(mode='w+t', delete=False) as f:
            f.write(content)
            tmp_path = Path(f.name)
        
        try:
            config = Config(tmp_path)
            self.assertEqual(config._vars, return_value)
        finally:
            tmp_path.unlink()
    
    def test_load_empty(self):
        # required non-exist-path
        path = Path('not a path!')
        if path.exists():
            raise Exception(f"path exists. {path}")
        
        config = Config(path)
        self.assertEqual(config._vars, MOCK_CONFIG)
    
    def test_set_attr(self):
        first_flag = False
        second_flag = False

        content = 'FIRST_VAR="first_value"; SECOND_VAR="second_value"'
        
        with NamedTemporaryFile(mode='w+t', delete=False) as f:
            f.write(content)
            tmp_path = Path(f.name)
        
        try:
            config = Config(tmp_path)

            if config.first_var == 'first_value':
                first_flag = True
            
            if config.second_var == 'second_value':
                second_flag = True
            
            self.assertTrue(all([first_flag, second_flag]))
        finally:
            tmp_path.unlink()
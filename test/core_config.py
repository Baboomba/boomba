import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from unittest.mock import patch, MagicMock
import configparser
from core.builder.config import ConfigFileReader, ConfigLoader

class TestConfigFileReader(unittest.TestCase):
    
    def test_get_conf_path_valid(self):
        config_reader = ConfigFileReader("db")
        path = config_reader._get_conf_path("db")
        expected_path = Path("./config/db.ini")
        self.assertEqual(path, expected_path)
    
    @patch("pathlib.Path.exists")
    def test_get_conf_path_invalid(self, mock_exists):
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            config_reader = ConfigFileReader("It is not a file name!!!")
    
    @patch("pathlib.Path.exists")
    @patch.object(configparser.ConfigParser, "read")
    def test_read_file_valid(self, mock_read, mock_exists):
        mock_exists.return_value = True
        mock_read.return_value = None
        
        config_reader = ConfigFileReader("db")
        config_reader._read_file("db")
        
        mock_read.assert_called_once()

    def test_content_valid(self):
        conf_reader = ConfigFileReader("db")
        conf_reader._conf.read_dict({
            "section1": {"key1": "value1", "key2": "value2"}
        })
        
        content = conf_reader.content("section1")
        
        self.assertEqual(content, {"key1": "value1", "key2": "value2"})
    
    def test_content_invalid_section(self):
        conf_reader = ConfigFileReader("db")
        conf_reader._conf.read_dict({
            "section1": {"key1": "value1", "key2": "value2"}
        })
        
        with self.assertRaises(KeyError):
            conf_reader.content("non_existing_section")


class TestConfigLoader(unittest.TestCase):

    @patch("os.path.exists")
    @patch.object(configparser.ConfigParser, "read")
    def test_dynamic_attr_setting(self, mock_read, mock_exists):
        mock_exists.return_value = True
        mock_read.return_value = None
        
        config_loader = ConfigLoader("db", "section1")
        
        # ConfigLoader가 동적으로 속성을 설정했는지 확인
        config_loader._conf.read_dict({
            "section1": {"key1": "value1", "key2": "value2"}
        })
        
        # 속성이 객체에 추가되었는지 확인
        self.assertEqual(config_loader.key1, "value1")
        self.assertEqual(config_loader.key2, "value2")


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from unittest.mock import patch

from argparse import ArgumentParser, Namespace
from io import StringIO

from boomba.cli.base import BaseCommand
from boomba.cli.description import ERROR


class TestBaseCommand(unittest.TestCase):
    
    def setUp(self):
        sys.argv = ['test', '--name', 'test_name']
        class TempCommand(BaseCommand):
            _description = 'test description'
            _epilog = 'test epilog'

            def add_all(self):
                self._parser.add_argument(
                    "--name",
                    required=True
                )
        
        self.inst = TempCommand()
    
    def test_create_parser(self):
        self.assertIsInstance(self.inst._parser, ArgumentParser)
        self.assertEqual(self.inst._parser.description, 'test description')
        self.assertEqual(self.inst._parser.epilog, 'test epilog')
    
    def test_create_subparser(self):
        self.assertIsNotNone(self.inst._subparser)
    
    def test_add_all_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            class InCompleteCommand(BaseCommand):
                _description = 'test_incoplete_description'
                _epilog = 'test_incomplete_epilog'
                pass
            InCompleteCommand()
    
    @patch('argparse.ArgumentParser.parse_args', return_value=Namespace(name='test_name'))
    def test_parse(self, mock):
        args = self.inst.parse()
        self.assertEqual(args.name, 'test_name')
    
    @patch('argparse.ArgumentParser.parse_args', return_value=Namespace(command='test_commnad'))
    def test_get_commnad(self, mock):
        self.inst._args = mock.return_value
        self.assertEqual(self.inst.get_command(), 'test_commnad')
    
    @patch('argparse.ArgumentParser.parse_args', return_value=Namespace(test='test_option'))
    def test_get_option_vaild_case(self, mock):
        self.inst._args = mock.return_value
        self.assertEqual(self.inst.get_option('--test'), 'test_option')
    
    @patch('argparse.ArgumentParser.parse_args', return_value=Namespace(test=None))
    @patch('sys.stdout', new_callable=StringIO)
    def test_get_option_invalid_case(self, mock_out, mock_args):
        self.inst._args = mock_args.return_value
        self.assertIsNone(self.inst.get_option('--test'))
        self.assertIn(ERROR['empty_args'], mock_out.getvalue())
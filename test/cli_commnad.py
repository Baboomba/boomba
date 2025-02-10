import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest
from unittest.mock import patch, MagicMock

from argparse import ArgumentParser, Namespace
from io import StringIO

from boomba.cli.command import CommandRegistor, CommandHandler
from boomba.cli.description import HELP

class TestRegistor(unittest.TestCase):

    def setUp(self):
        sys.argv = ['startproject']
        self.inst = CommandRegistor()
    
    def test_add_startproject(self):
        self.inst._subparser = MagicMock()
        self.inst.add_startproject()
        self.inst._subparser.add_parser.assert_called_with(
            self.inst.startproject,
            help=HELP[self.inst.startproject]
        )
    
    def test_add_initdb(self):
        self.inst._subparser = MagicMock()
        self.inst.add_initdb()
        self.inst._subparser.add_parser.assert_called_with(
            self.inst.initdb,
            help=HELP[self.inst.initdb]
        )
    
    def test_add_run(self):
        self.inst._subparser = MagicMock()
        self.inst.add_run()
        self.inst._subparser.add_parser.assert_called_with(
            self.inst.run,
            help=HELP[self.inst.run]
        )
    
    def test_add_createpipe(self):
        parser_flag = False
        option_flag = False
        
        if self.inst.createpipe in self.inst._subparser.choices:
            parser_flag = True
        
            subparser = self.inst._subparser.choices[self.inst.createpipe]
            for action in subparser._actions:
                print(action.dest)
                if action.dest == 'name':
                    option_flag = True
                    break
        self.assertTrue(all([parser_flag, option_flag]))
    
    def test_add_test(self):
        parser_flag = False
        option_flag = False
        
        if self.inst.test in self.inst._subparser.choices:
            parser_flag = True
        
            subparser = self.inst._subparser.choices[self.inst.test]
            for action in subparser._actions:
                print(action.dest)
                if action.dest == 'name':
                    option_flag = True
                    break
        self.assertTrue(all([parser_flag, option_flag]))
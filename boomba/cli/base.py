from argparse import (
                ArgumentParser,
                RawTextHelpFormatter,
                Namespace,
                _SubParsersAction
            )

from boomba.cli.description import ERROR


class BaseCommand:
    _description: str
    _epilog: str
    _parser: ArgumentParser
    _subparser: _SubParsersAction
    _args: Namespace
    
    # base command
    command: str = 'command'
    
    def __init__(self):
        self._create_parser()
        self._create_subparser()
        self.add_all()
        self.args = self.parse()
    
    def _create_parser(self) -> None:
        self._parser = ArgumentParser(
            description=self._description,
            epilog=self._epilog,
            formatter_class=RawTextHelpFormatter
        )
        
    def _create_subparser(self) -> None:
        self._subparser = self._parser.add_subparsers(
            dest='command',
            help='Available commands'
        )

    def add_all(self) -> None:
        '''
        Adds all the required arguments at once to the parser.\n
        This method acts like an abstract method.
        
        Example
        -------
        ```python
        # must implement this method as shown below
        def add_all(self) -> None:
            self.parser.add_argument('--name')
            self.parser.add_argument('--age', type=int)
        ```
        '''
        raise NotImplementedError(
            "Subclasses must implement this method to define arguments."
        )

    def parse(self):
        return self._parser.parse_args()

    def get_command(self) -> str:
        if self.args is None:
            print(ERROR['empty_args'])
        return getattr(self.args, self.command, None)
    
    def get_option(self, key: str) -> str:
        if self.args is None:
            print(ERROR['empty_args'])
        return getattr(self.args, key.replace('-', ''), None)
    
    def help(self):
        self._parser.print_help()
from pathlib import Path
import warnings

from sqlalchemy import inspect

from boomba.cli.base import BaseCommand
from boomba.cli.description import (
    HEADER,
    HELP,
    MESSAGE,
    CHECK,
    ERROR
)
from boomba.core.config import Config
from boomba.core.constants import DATA_DIR
from boomba.core.db import Connector
from boomba.core.metadata import Base
from boomba.core.schedule import Job, _register_jobs
from boomba.exception.exc import (
    NonEmptyDirectoryError,
    DatabaseConfigurationError,
    EmptyArgumentError
)
from boomba.template.template import Generator




class CommandRegistor(BaseCommand):
    _description = HEADER['description']
    _epilog = HEADER['epilog']
    
    # commands
    startproject: str = 'startproject'
    run: str = 'run'
    createpipe: str = 'createpipe'
    name: str = 'name'
    initdb: str = 'initdb'
    test: str = 'test'
    
    # valid options
    _list_default = 'all'
    
    def add_all(self) -> None:
        self.add_startproject()
        self.add_run()
        self.add_createpipe()
        self.add_initdb()
        self.add_test()
    
    def add_startproject(self) -> None:
        self._subparser.add_parser(
            self.startproject,
            help=HELP[self.startproject]
        )
    
    def add_initdb(self) -> None:
        self._subparser.add_parser(
            self.initdb,
            help=HELP[self.initdb]
        )
    
    def add_run(self) -> None:
        self._subparser.add_parser(
            self.run,
            help=HELP[self.run]
        )
    
    def add_createpipe(self) -> None:
        self._subparser.add_parser(
            self.createpipe,
            help=HELP[self.createpipe]
        ).add_argument(
            self.name,
            type=str,
            help=self.name
        )
    
    def add_test(self) -> None:
        self._subparser.add_parser(
            self.test,
            help=HELP[self.test]
        ).add_argument(
            self.name,
            type=str,
            help=self.name
        )


class CommandHandler(CommandRegistor):
    
    def __init__(self):
        super().__init__()
        self.generator = Generator()
        self.handle()
    
    def handle(self) -> None:
        command = self.get_command()
        
        if command == self.run:
            self.run_command()
        elif command == self.createpipe:
            self.createpipe_command()
        elif command == self.startproject:
            self.startproject_command()
        elif command == self.initdb:
            self.initdb_command()
        elif command == self.test:
            self.test_command()
        else:
            raise EmptyArgumentError()
    
    def startproject_command(self) -> None:
        if any(Path.cwd().iterdir()):
            raise NonEmptyDirectoryError()
        
        self.generator.init_directories()
        print(MESSAGE['startproject'])
    
    def initdb_command(self) -> None:
        conf = Config()
        if conf.is_mock:
            warnings.warn(CHECK['start'])
            return
        
        connector = Connector(conf.base_db, echo=True)
        
        ins = inspect(connector.engine)
        tables = ins.get_table_names()
        if tables:
            warnings.warn(CHECK['table_exist'].format(tables))
        
        Base.metadata.create_all(connector.engine)
        print(MESSAGE['initdb'])
    
    def run_command(self) -> None:
        print(MESSAGE['initial'])
        conf = Config()
        
        # get the load directory
        print(CHECK['data_dir'].format(DATA_DIR))
        
        # check db
        db = conf.database[conf.base_db]
        if db['drivername'] == 'sqlite':
            db_ip = 'sqlite:///' + db['database']
        else:
            db_ip = db['host']
        
        connector = Connector(conf.base_db)
        try:
            with connector.engine.connect() as conn:
                conn.close()
                print(CHECK['database'].format(db_ip))
        except:
            raise DatabaseConfigurationError()
        
        job = Job()
        job.run()
    
    def createpipe_command(self) -> None:
        self.generator.create_pipeline(self._args.name)
    
    def test_command(self) -> None:
        _register_jobs()
        job = Job()
        for j in job.job_list:
            if j.name == self._args.name:
                print(MESSAGE['start_test'].format(j.name))
                try:
                    j.loader()
                    print(MESSAGE['end_test'])
                    return
                except RuntimeError as e:
                    raise print(e)
        print(ERROR['invalid_job_name'].format(self._args.name))
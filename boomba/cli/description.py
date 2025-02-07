from typing import Dict
from boomba.core.constants import PYTHON_VERSION, BOOMBA_VERSION


HEADER: Dict[str, str] = {
    'description': (
        "Boomba is a lightweight and efficient ETL pipeline framework.\n\n"
        "Features:\n"
        "- Schedule and automate ETL jobs\n"
        "- Support for data extraction, transformation, and loading tasks\n"
        "- Build efficient data pipelines with ease\n\n"
        "[Example Usage]:\n"
        " $ boomba startproject\n"
        " $ boomba run\n"
        " $ boomba createpipe <pipe_name>\n"
    ),
    
    'epilog': (
        "[Detailed Job Information]\n"
        "If you want to check more detailed job statuses,\n"
        "please connect to the database specified in the configuration file.\n"
        "In the database, you can view the execution time and results of jobs,\n"
        "the paths of generated files, the status of the current job queue,\n"
        "and the list of jobs created today. \n\n"
        "For more information,\n"
        " - github : https://github.com/Baboomba/boomba\n"
        " - email  : bach0918@gmail.com"
    ),
}

HELP: Dict[str, str] = {
    'startproject': 'Create boomba project(no additional arguments)',
    
    'initdb': 'Initiate database for boomba systme(not for extraction)',
    
    'run': 'Execute boomba application(no additional arguments)',
    
    'createpipe': (
        "Create a new pipeline (requires a string argument,\n"
        "the additional argument is set as the pipeline name)"
    ),
    
    'name': 'Pipeline name to create',
    
    '--list': (
        "List the registered queue (if no string argument is provided,\n"
        "all jobs will be displayed; if an argument is provided,\n"
        "only that job will be shown)"
    ),
}

MESSAGE: Dict[str, str] = {
    'initial': (
        "=============================================\n"
        f"Boomba v{BOOMBA_VERSION} = Startup\n"
        "=============================================\n"
        "Initializing Boomba framework...\n"
        f"Python version: {PYTHON_VERSION}\n"
    ),    
}

CHECK: Dict[str, str] = {
    'data_dir': "Default data directory: {}",
    
    'database': 'Base database has successfully connected to IP adress : {}',
    
    'table_exist': 'tables already exist. [Table] {}',
    
    'start': 'Please start a project first.'
}

ERROR: Dict[str, str] = {
    'invalid_args': "Invalid argument. Please, read help(--help)",
    'empty_args': (
        "No arguments were provided. Please refer to the help.\n"
        " $ boomba --help"
    ),
}
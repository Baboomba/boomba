from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from http.client import HTTPResponse
from io import BytesIO
import json
from pathlib import Path
from typing import List, Union, Dict, TYPE_CHECKING
from urllib import request

import polars as pl
import pyarrow.parquet as pq

if TYPE_CHECKING:
    try:
        import boto3
        from botocore.exceptions import ClientError
    except:
        raise ModuleNotFoundError("Did you install boto3?")

from boomba.core.db import DBManager
from boomba.core.schema import Schema
from boomba.core.config import Config, Conf
from boomba.core.constants import (
    PIPELINE_DIR,
    DATA_DIR,
    ACCEPT_HEADERS,
    CONTENT_HEADERS,
    ENCODING,
    BASE_DATA_FORMAT
)
from boomba.exception.exc import (
    ModuleLocationError,
    PipeNotFoundError,
    UndefinedAttributeError,
    ConfigurationError
)
from boomba.util.parse import to_snake_case, to_date_format


__all__ = [
    'DBExtractor',
    'Transformer',
    'Loader'
]


class Extractor(ABC):
    data: pl.DataFrame
    schema: Schema
    
    def __init__(self) -> None:
        self._check_attr()
        self.data = self._extract_data()
    
    @abstractmethod
    def _check_attr(self) -> None: ...
    
    @abstractmethod
    def _extract_data(self) -> pl.DataFrame: ...
    
    def _to_dataframe(self, df: pl.DataFrame) -> pl.DataFrame:
        if hasattr(self, 'schema'):
            return pl.DataFrame(df, schema=self.schema().schema)
        
        return pl.DataFrame(df)
    

class DBExtractor(Extractor):
    """
    A base class for extracting data from a database and returning it as a DataFrame.

    This class provides the core functionality for extracting data from a database using 
    a configured query and parameters, and returning the result as a `pl.DataFrame`. It 
    expects a schema and a query to be provided and requires a valid database configuration 
    to be initialized.
    
    Attributes
    ---
        db_name (str): The database configuration section name.
        schema (Schema): The schema for the data being extracted.
        query (str): The SQL query to be executed.
        query_params (str): The parameters for the query.
        data (pl.DataFrame): The extracted data from database

    """
    db_name: str
    query: str
    query_params: str = None
    
    def _check_attr(self) -> None:
        db_name = 'db_name'
        query = 'query'
        schema = 'schema'
        
        if not hasattr(self, db_name):
            raise UndefinedAttributeError(self, db_name)
            
        if not hasattr(self, query):
            raise UndefinedAttributeError(self, query)
        
        if hasattr(self, schema):
            if not issubclass(self.schema, Schema):
                raise TypeError(
                    ("Invalid type for 'schema'. "
                    "Expected subclass of Schema.")
                )
    
    def _create_dbmanager(self, db: DBManager=None) -> None:
        self._db = db or DBManager(self.db_name)
     
    def _extract_data(self) -> pl.DataFrame:
        self._create_dbmanager()
        try:
            result = self._db.select(self.query, self.query_params, False)
            return self._to_dataframe(result)
        except Exception as e:
            raise RuntimeError(str(e))


class FileExtractor(Extractor):
    pipe_name: str
    collection: str
    start: str
    end: str
    file_name: str
    format: str
    
    def _check_attr(self) -> None:
        ...
    
    def _extract_data(self) -> pl.DataFrame:
        ...


class APIExtractor(Extractor):
    url: str
    method: str
    payload: str
    
    def _check_attr(self) -> None:
        url = 'url'
        method = 'method'
        payload = 'payload'
        
        if not hasattr(self, url):
            raise UndefinedAttributeError(self, url)
        
        if not hasattr(self, method):
            self.method = self.method.upper()
        else:
            raise UndefinedAttributeError(self, method)
            
        if self.method not in ['GET', 'POST']:
            raise ValueError(
                "http method must be one of 'get', or 'post'."
            )
        
        if self.method == 'POST':
            if not hasattr(self, payload):
                raise UndefinedAttributeError(self, payload)
    
    def _parse_json(self, res: HTTPResponse) -> pl.DataFrame:
        try:
            data = res.read().decode()
            return pl.DataFrame(json.loads(data))
        except Exception as e:
            raise RuntimeError(str(e))
    
    def _get(self) -> pl.DataFrame:
        req = request.Request(
            self.url,
            headers=ACCEPT_HEADERS,
            method=self.method
        )
        with request.urlopen(req) as res:
            return self._to_dataframe(self._parse_json(res))
    
    def _post(self) -> pl.DataFrame:
        data = json.dumps(self.payload).encode(ENCODING)
        req = request.Request(
            self.url,
            data=data,
            headers=CONTENT_HEADERS,
            method=self.method
        )
        with request.urlopen(req) as res:
            return self._to_dataframe(self._parse_json(res))

    def _extract_data(self) -> pl.DataFrame:
        if self.method == 'GET':
            self.data = self._get()
        else:
            self.data = self._post()
    

class Transformer:
    """
    Abstract base class for extracting and processing data.

    The `Transformer` class provides the structure for implementing data extraction 
    and processing workflows. It defines an abstract method `process_data()` that 
    must be implemented in subclasses. Data is fetched using the `extractor` attribute, 
    processed via the `process_data()` method, and validated to ensure correctness.

    Attributes
    ----------
    extractor : Union[List[DBExtractor], DBExtractor]
        The object or list of objects responsible for extracting data.
    data : pl.DataFrame
        The raw data extracted by the extractor(s).
    result : Optional[Union[Dict[str, pl.DataFrame], pl.DataFrame]]
        The processed result after applying `process_data()`.
    """
    extractor: Union[List[DBExtractor], Extractor]
    
    def __init__(self) -> None:
        self.data = self._get_extracted_data()
        self.result = self._validate_process_data()
    
    def _get_extracted_data(self) -> Union[Dict[str, pl.DataFrame], pl.DataFrame]:
        """
        Extracts data using the `extractor` attribute.
        
        Returns
        -------
        Union[Dict[str, pl.DataFrame], pl.DataFrame]
        - a dictionary where keys are the name of subclasses of Extractor class,
        and values are the extracted data as `pl.DataFrame` for each class.
        """
        if not hasattr(self, 'extractor'):
            raise UndefinedAttributeError(self, 'extractor')
        
        data_map = {}
                
        if isinstance(self.extractor, list):
            if not all(issubclass(item, DBExtractor) for item in self.extractor):
                raise TypeError("All items in the list must be of type DBExtractor.")
        
        elif issubclass(self.extractor, Extractor):
            self.extractor = [self.extractor]
        else:
            raise TypeError(
                "extractor must be a List[Extractor] or a Extractor."
            )
        
        try:
            for cls in self.extractor:
                inst = cls()
                data_map[inst.__class__.__name__.lower()] = inst.data
        except Exception as e:
            raise RuntimeError(str(e))
        
        return data_map
    
    def _validate_process_data(self) -> pl.DataFrame:
        """
        Calls the `process_data()` method and validates the result.
        This method raises a `TypeError` if the `process_data()` method returns `None`.
        """
        result = self.process_data()
        
        if result is None:
            raise NotImplementedError(
                (f"Class {self.__class__.__name__} must implement "
                 "the 'process_data' method, "
                 "and return a DataFrame.")
            )
        
        if not isinstance(result, pl.DataFrame):
            raise TypeError(
                "The result produced by the 'process_data()' method "
                "must be of type 'pl.DataFrame'."
            )
        
        return result
        
    def process_data(self) -> pl.DataFrame:
        """
        Abstract method. This method must be implemented to process the data.
        
        This method must be implemented in subclasses of `Transformer`.
        If not implemented, a `TypeError` will be raised.
        """
        pass


class Loader(ABC):
    """
    A class responsible for loading and processing data within a pipeline.
    
    Attributes
    -----
    - section (str): The configuration section to be used(required).
    - schema (Schema): The schema for loading the data(optional).
    - transformer (Transformer): The subclass of transformer class used to process the data(required).
    """
    schema: Schema
    transformer: Transformer
    collection: str
    file_name: str
    pipe_name: str
    location: Path
    path: str
    
    def __init__(self, conf: Config=Conf) -> None:
        self._check_attr()
        self._conf = conf
        self._additional_init_()
        self.pipe_name = self._get_pipe_name()
        self.collection = self._set_collection()
        self.location = self._set_location()
        self.path = self._set_path()
        self._load_data()
        
    def __repr__(self) -> str:
        return (
            f"Loader(pipe_name={self.pipe_name}, "
            f"collection={self.collection}, "
            f"file_name={self.file_name})"
        )
    
    @abstractmethod
    def _additional_init_(self) -> None: ...
    
    @abstractmethod
    def _set_path(self) -> str: ...
    
    @abstractmethod
    def _load_data(self) -> None: ...
    
    def _check_attr(self) -> None:
        transformer = 'transformer'
        collection = 'collection'
        
        if not hasattr(self, transformer):
            raise UndefinedAttributeError(self, transformer)
        else:
            if not isinstance(self.transformer, type) or not issubclass(self.transformer, Transformer):
                raise TypeError(
                    ("Invalid type for 'transformer'. "
                    "Expected instance of 'Transformer'.")
                )
            
        if hasattr(self, collection):
            if not isinstance(self.collection, str):
                raise TypeError(
                    ("Invalid type for 'collection'. "
                    "Expected instance of 'str'.")
                )
    
    def _get_pipe_name(self) -> str:
        """
        Raises
        -----
            RuntimeError: If the Location class is used outside of a valid pipeline.
        """
        module = self.__module__ 
        token = module.split('.')
        
        if token[0] != PIPELINE_DIR.name:
            raise ModuleLocationError(self, additional_msg=module)
        
        if len(token) == 1:
            raise PipeNotFoundError(self)
        
        return token[1]
    
    def _set_collection(self) -> str:
        if not hasattr(self, 'collection'):
            return to_snake_case(self.__class__.__name__)
        return self.collection.lower()
    
    def _set_location(self) -> Path:
        return Path(self.pipe_name) / self.collection


class FSType(Enum):
    local = 'local'
    s3 = 's3'
        

class FSLoader(Loader):
    fs_name: str
    _fs_type: str
    bucket: str
    
    def _additional_init_(self) -> None:
        self.fs_name = self._set_fs_name()
        self._fs_type = self._get_fs_type()
        self.bucket = self._set_bucket()
        self._s3 = self._get_s3_client()
        
    def _set_fs_name(self) -> str:
        if not hasattr(self, 'fs_name'):
            return self._conf.base_fs
        return self.fs_name
    
    def _get_fs_type(self) -> str:
        return self._conf.file_system[self.fs_name]['fs_type']
    
    def _set_bucket(self) -> str:
        if self._fs_type == FSType.local.value:
            if hasattr(self, 'bucket'):
                raise AttributeError(
                    "Not allowed to set bucket on the local system"
                )
        elif self._fs_type == FSType.s3.value:
            if not hasattr(self, 'bucket'):
                self.bucket = self._conf.file_system[self.fs_name]['bucket']
            return self.bucket
        else:
            raise ValueError(f"Invalid 'fs_type'. Not allow {self._fs_type}")
    
    def _get_s3_client(self):
        '''Import boto3 only when using S3 (not a default dependency package).'''
        try:
            global boto3, ClientError
            if self._fs_type == FSType.s3.value:
                import boto3 as boto3_
                from botocore.exceptions import ClientError as ClientError_
                boto3 = boto3_
                ClientError = ClientError_
                
                try:
                    access_id = self._conf.file_system[self.fs_name]['access_id']
                    access_key = self._conf.file_system[self.fs_name]['access_key']
                    region = self._conf.file_system[self.fs_name]['region']
                except:
                    raise ConfigurationError(self, additional_msg='Access info for s3.')
                return boto3.client(
                    FSType.s3.value,
                    aws_access_key_id=access_id,
                    aws_secret_access_key=access_key,
                    region_name=region
                )
        except Exception as e:
            raise RuntimeError(str(e))
    
    def _set_path(self) -> str:
        if not hasattr(self, 'file_name'):
            format = to_date_format(self._conf.file_date_format)
            self.file_name = {datetime.now().strftime(format)}
        
        self.file_name = f'{self.file_name}.{BASE_DATA_FORMAT}'
        
        if self._fs_type == FSType.local.value:
            dir = DATA_DIR / self.location
            dir.mkdir(parents=True, exist_ok=True)
            path = dir / self.file_name
            
            if not self._conf.file_system[self.fs_name]['allow_overwrite']:
                if path.exists():
                    raise FileExistsError(
                        "Already exsits the same file in the path : "
                        f"'{str(path)}'"
                    )
        elif self._fs_type == FSType.s3.value:
            path = str(self.location / self.file_name).replace('\\', '/')
            if not self._conf.file_system[self.fs_name]['allow_overwrite']:
                try:
                    self._s3.head_object(Bucket=self.bucket, Key=path)
                    raise FileExistsError(
                        "Already exsits the same file in the path : "
                        f"'{str(path)}'"
                    )
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        pass
        
        return str(path)
      
    def _load_data(self) -> None:
        transformer: Transformer = self.transformer()
        data = transformer.result
        
        if hasattr(self, 'schema'):
            data = pl.DataFrame(
                data,
                schema=self.schema().schema
            )
        else:
            data = pl.DataFrame(data)
        
        if self._fs_type == FSType.local.value:
            data.write_parquet(self.path)
        elif self._fs_type == FSType.s3.value:
            buffer = BytesIO()
            pq.write_table(data.to_arrow(), buffer)
            buffer.seek(0)
            self._s3.put_object(
                Bucket=self.bucket,
                Key=self.path,
                Body=buffer.read())
            

class DBLoader(Loader):
    table_name: str
    db_name: str
    
    def _additional_init_(self) -> None:
        if not hasattr(self, 'table_name'):
            raise UndefinedAttributeError(self, additional_msg='table_name')
        
        if not hasattr(self, 'db_name'):
            raise UndefinedAttributeError(self, additional_msg='db_name')
    
    def _set_path(self) -> None:
        return self.table_name
    
    def _load_data(self) -> None:
        db = DBManager(self.db_name)
        transformer: Transformer = self.transformer()
        data = transformer.result
        db.insert(data, self.table_name)
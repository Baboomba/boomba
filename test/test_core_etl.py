import pytest
from pathlib import Path
import polars as pl
from tempfile import NamedTemporaryFile

from boomba.core.db import DBManager
from boomba.core.config import Config
from boomba.core.dtypes import Dtype
from boomba.core.etl import (
    Extractor,
    DBExtractor,
    APIExtractor,
    Transformer,
    Loader,
    DBLoader,
    FSLoader
)
from boomba.core.schema import Schema


def test_extractor():
    class TestSchema(Schema):
        name = Dtype.String()
        age = Dtype.UInt8()

    class TestExtractor(Extractor):
        schema = TestSchema
        
        def _check_attr(self):
            pass

        def _extract_data(self):
            return pl.DataFrame({
                "name": ["Alice", "Bob", "Paul"],
                "age": [20.0, 30.0, 40.0]
            })
    
    test = TestExtractor()
    expected_value = [('name', pl.String), ('age', pl.Float64)]
    assert list(test.data.schema.items()) == expected_value
    test.data = test._to_dataframe(test.data)
    expected_value = [('name', pl.String), ('age', pl.UInt8)]
    assert list(test.data.schema.items()) == expected_value


@pytest.fixture
def prepare_test_config():
    
    content = '''
DATABASE = {
    'test': {
        'drivername': 'sqlite',
        'database': ':memory:'
    },
}
'''
    with NamedTemporaryFile(mode='w+t', delete=False) as f:
        f.write(content)
        tmp_path = Path(f.name)
    
    yield Config(tmp_path)
    tmp_path.unlink()


def test_dbextractor_sqlite(prepare_test_config):
    db = DBManager('test', prepare_test_config)
    data = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "age": [20.0, 30.0, 40.0]
    })
    db.insert(data, 'test_table')

    class TestExtractor(DBExtractor):
        db_name = 'test'
        query = 'SELECT * FROM test_table'
        _db = db
    
    extractor = TestExtractor()
    assert extractor.data.equals(data)


def test_apiextractor():
    class TestAPI(APIExtractor):
        url = "https://jsonplaceholder.typicode.com/posts/1"
        method = 'GET'

    test = TestAPI()
    expect = {
        "userId": 1,
        "id": 1,
        "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
        "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
    }
    assert len(test.data) > 0
    assert test.data.equals(pl.from_dict(expect))


def test_transformer(prepare_test_config):
    db = DBManager('test', prepare_test_config)
    data = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "age": [20.0, 30.0, 40.0]
    })
    db.insert(data, 'users')
    data = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "height": [160, 170, 180]
    })
    db.insert(data, 'health')

    class Users(DBExtractor):
        db_name = 'test'
        query = 'SELECT * FROM users'
        _db = db
    
    class Health(DBExtractor):
        db_name = 'test'
        query = 'SELECT * FROM health'
        _db = db
    
    class TestTransformer(Transformer):
        extractor = [Users, Health]

        def process_data(self):
            users = self.data['Users']
            health = self.data['Health']
            return users.join(health, on='name')
    
    transformer = TestTransformer()
    expect = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "age": [20.0, 30.0, 40.0],
        "height": [160, 170, 180]
    })
    assert transformer.result.equals(expect)


def test_loader():
    path = Path.cwd() / 'pipeline' / 'test'
    path.mkdir(parents=True, exist_ok=True)
    
    class TestLoader(Loader):
        transformer = Transformer
        _module_setter_for_test = 'pipeline.test'
        
        def _additional_init_(self):
            pass
        
        def _set_path(self):
            pass
        
        def _load_data(self):
            pass
    
    loader = TestLoader()
    assert loader.pipe_name == 'test'
    assert loader.collection == 'test_loader'
    assert loader.location == 'test/test_loader'


def test_dbloader():
    db = DBManager('test', prepare_test_config)
    data = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "age": [20.0, 30.0, 40.0]
    })
    db.insert(data, 'users')
    data = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "height": [160, 170, 180]
    })
    db.insert(data, 'health')

    class Users(DBExtractor):
        db_name = 'test'
        query = 'SELECT * FROM users'
        _db = db
    
    class Health(DBExtractor):
        db_name = 'test'
        query = 'SELECT * FROM health'
        _db = db
    
    class TestTransformer(Transformer):
        extractor = [Users, Health]

        def process_data(self):
            users = self.data['Users']
            health = self.data['Health']
            return users.join(health, on='name')
    
    class TestLoader(DBLoader):
        db_name = 'test'
        table_name = 'load_result'
        transformer = TestTransformer
    
    TestLoader(prepare_test_config)
    data = db.select('SELECT * FROM load_result')
    expect = pl.DataFrame({
        "name": ["Alice", "Bob", "Paul"],
        "age": [20.0, 30.0, 40.0],
        "height": [160, 170, 180]
    })
    assert data.equals(expect)


@pytest.mark.skip(reason="Not yet inplemented.")
def test_fsloader():
    pass
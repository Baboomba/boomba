from typing import List, Union

import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Row, Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError

from boomba.core.config import Conf, Config


__all__ = ['DBManager']


class Connector:
    """
    A database connector that creates and manages SQLAlchemy engines.

    This class uses DBConfig to load and validate configuration settings, 
    and then generates connection strings and SQLAlchemy engines for database interaction.

    Attributes:
        __conf (DBConfig): The configuration object for the database connection.

    Args:
        section (str): The name of the configuration section to load.
    """

    def __init__(self, db_name: str, conf: Config=Conf) -> None:
        self._db_name = db_name
        self._conf = conf
        self.engine = self._create_engine()
    
    def _get_conn_str(self) -> str:
        fields = self._conf.database[self._db_name]
        return URL.create(**fields)

    def _create_engine(self) -> Engine:
        connection_string = self._get_conn_str()
        engine = create_engine(connection_string)
        return engine


class DBManager(Connector):
    """
    A database manager that provides methods for executing SELECT, UPDATE, DELETE, and INSERT queries.
    This class also supports transaction handling.

    Parameter
    ---
    section (str): The name of the configuration section to load.

    Example:
        ```python
        # Example usage
        db_manager = DBManager("my_database_section")
        query = "SELECT name, age FROM some_table"
        db_manager.select(query)
        ```
    Attributes
    ---
    - engine (Engine): The SQLAlchemy engine for database connection.
    """

    def __init__(self, db_name: str):
        super().__init__(db_name)
        
    def execute_query(self, query: str, params: dict = None) -> None:
        """
        Executes a raw SQL query on the database.
        
        Parameters
        ---
        - query (str): The SQL query to be executed.
        - params (dict, optional): A dictionary of parameters to bind to the query. Defaults to None.

        Example
        ---
        ```python
        db_manager = DBManager("my_database_section")
        query = "UPDATE users SET age = :age WHERE name = :name"
        params = {"name": "Alice", "age": 30}
        db_manager.execute(query, params)
        ```
        
        Notes
        ---
        - This method does not return any data; it simply executes the provided SQL query.
        - If the query is a SELECT, it will not return results.
        - If the query involves a modification (INSERT, UPDATE, DELETE), it will be committed immediately.
        """
        with self.engine.begin() as connection:
            connection.execute(text(query), params or {})

    def select(self, query: str, params: dict = None, to_df: bool=True) -> Union[pl.DataFrame, List[Row]]:
        """
        Executes a SELECT query and returns the results, either as a list of rows or a Polars DataFrame.

        Parameters
        ----------
        - query (str): The SQL query to execute.
        - params (dict, optional): A dictionary of parameters to bind to the query. Defaults to None.
        - to_df (bool, optional): If True, the result will be returned as a Polars DataFrame. If False, a list of rows is returned. Defaults to True.
            
        Example
        -------
        ```python
        db_manager = DatabaseManager(connector)
        query = "SELECT * FROM users WHERE age > :age"
        params = {"age": 30}
        results = db_manager.select(query, params, to_df=True)
        print(results)
        ```

        Returns
        -------
        - If `to_df` is True, returns a Polars DataFrame containing the query result.
        - If `to_df` is False, returns a list of rows (each row is a SQLAlchemy Row object).

        Raises
        ------
        - RuntimeError: If there is an error during the SQL query execution.
        """
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            
            if to_df:
                return self._to_DataFrame(result)
            
            return result.fetchall()

    def insert(
            self,
            df: pl.DataFrame,
            table_name: str,
            if_exists: str = "append",
            chunksize: int = 100000
        ) -> None:
        """
        Inserts a Polars DataFrame into a database table using Polars' write_database method.

        Parameters
        ----------
        df : pl.DataFrame
            The Polars DataFrame to insert into the database.
        table_name : str
            The name of the target table in the database.
        if_exists : str, optional
            Behavior when the table already exists. Options are:
            - 'fail': raises an error (default)
            - 'replace': drops the table and recreates it
            - 'append': appends the data to the existing table
        chunksize : int, optional
            The number of rows to insert in each batch. Default is 100000.

        Example
        -------
        ```python
        df = pl.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
        db_manager = DBManager("mydb")
        db_manager.insert(df, "users", if_exists="append")
        ```

        Raises
        ------
        RuntimeError
            If there is an error while inserting the data into the database.
        """
        try:
            if not isinstance(df, pl.DataFrame):
                raise TypeError(
                    f"Expected a Polars DataFrame, but got '{type(df).__name__}' instead."
                )
            
            df.write_database(
                table_name=table_name,
                connection=self.engine,
                if_table_exists=if_exists,
                engine="sqlalchemy",
                engine_options={"chunksize": chunksize}
            )
        except Exception as e:
            raise RuntimeError(f"Failed to insert DataFrame into {table_name}: {e}")

    def transaction(self, queries: list):
        """
        Executes a list of queries within a transaction.

        Parameters
        ---
        - queries (list): A list of dictionaries containing 'query' and optional 'params'.
        
        Example
        ---
        ```python
            # Example usage of the transaction method
            queries = [
                {'query': 'INSERT INTO users (name, age) VALUES (:name, :age)', 'params': {'name': 'Alice', 'age': 30}},
                {'query': 'UPDATE users SET age = :age WHERE name = :name', 'params': {'name': 'Alice', 'age': 31}},
            ]
            try:
                db_manager = DatabaseManager(connector)
                db_manager.transaction(queries)
            except RuntimeError as e:
                print(f"Error: {e}")
        ```
        
        Raises:
            SQLAlchemyError: If an error occurs during the transaction.
        """
        with self.engine.begin() as connection:
            try:
                for q in queries:
                    connection.execute(text(q['query']), q.get('params', {}))
            except SQLAlchemyError as e:
                raise RuntimeError(f"Transaction failed: {e}")
            
    def _to_DataFrame(self, result: List[Row]) -> pl.DataFrame:
        """
        Converts a list of SQL query results into a Polars DataFrame.

        This method processes the result of a SQL query, extracts the column names, and converts the result
        into a Polars DataFrame.

        Parameters
        ----------
        - result (list): The query result as a list of rows (usually returned by SQLAlchemy).

        Example
        -------
        ```python
        query = "SELECT id, name FROM users"
        result = db_manager.select(query)
        df = db_manager._to_DataFrame(result)
        print(df)
        ```

        Returns
        -------
        - pl.DataFrame: A Polars DataFrame containing the query result.

        Raises
        ------
        - ValueError: If no data is returned from the query.
        - Exception: If there is an error while creating the Polars DataFrame.
        """
        if not result:
            raise ValueError("No data returned from the query.")
        
        try:
            return pl.DataFrame(result)
        except Exception as e:
            raise ValueError(f"Failed to create Polars DataFrame: {e}")
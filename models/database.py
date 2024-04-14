import sqlite3
import inspect
from pathlib import Path
from models.logger import logger

class SQLite:
    def __init__(self):
        """
        Initializes a SQLite database connection.

        Parameters:
        - logger: Logger object for logging
        """
        self.__initialize_resources(logger)

    @classmethod
    def __initialize_resources(cls, logger):
        """
        Initializes class-level resources.

        Parameters:
        - logger: Logger object for logging
        """
        try:
            current_path = Path(__file__).resolve()
            parent_path = current_path.parent.parent
            db_path = parent_path / f'database.db'
            cls._conn = sqlite3.connect(db_path, check_same_thread=False)
            cls._conn.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
            cls._cursor = cls._conn.cursor()
            cls._logger = logger
            logger.info(f"{cls._method_path()}: complete")
        except Exception as e:
            logger.error(f"{cls._method_path()}: {e}")
            exit()

    @classmethod
    def _method_path(cls):
        """
        Returns the path of the calling method.
        """
        return "{0}.{1}".format(cls.__name__, inspect.stack()[1][3])
    
    def execute(self, query:str, parameters:list=None):
        """
        Executes a SQL query with optional parameters.

        Parameters:
        - query: SQL query string
        - parameters: Optional parameters for the query

        Returns:
        - success: Boolean indicating whether the query was successful
        - result: Cursor object containing query result or error message
        """
        try:
            if parameters:
                self._cursor.execute(query, parameters)
            else:
                self._cursor.execute(query)
            self._conn.commit()
            return True, self._cursor
        except sqlite3.Error as e:
            return False, str(e)

db = SQLite()
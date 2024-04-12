import bcrypt
import inspect
from models.logger import logger
from models.database import db

class User:
    def __init__(self):
        """
        Initializes a User object.

        Parameters:
        - db: Database connection object
        - logger: Logger object for logging
        """
        self.__initialize_resources(db, logger)
        self.user_id = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.password = None

    @classmethod
    def __initialize_resources(cls, db, logger):
        """
        Initializes class-level resources.

        Parameters:
        - db: Database connection object
        - logger: Logger object for logging
        """
        cls._db = db
        cls._logger = logger

    @classmethod
    def _method_path(cls):
        """
        Returns the path of the calling method.
        """
        return "{0}.{1}".format(cls.__name__, inspect.stack()[1][3])
    
    def db_start(self):
        """
        Initializes the database schema if not exists.
        """
        success, result = self._db.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                "user_id"       INTEGER NOT NULL UNIQUE,
                "username"      TEXT NOT NULL UNIQUE,
                "first_name"    TEXT,
                "last_name"     TEXT,
                "password"      TEXT NOT NULL,
                "created_at"    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY("user_id" AUTOINCREMENT)
            );
        ''')
        if success:
            self._logger.info(f"{self._method_path()}: {success}")
        else:
            self._logger.error(f"{self._method_path()}: {result}")
            exit()

    @classmethod
    def _hash_password(cls, password:str):
        """
        Hashes the provided password using bcrypt.

        Parameters:
        - password: Plain text password to be hashed

        Returns:
        - hashed_password: Hashed password
        """
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
        return hashed_password
    
    def validate(self, password:str ):
        """
        Validates the provided password against the stored hashed password.

        Parameters:
        - password: Plain text password to be validated

        Returns:
        - success: Boolean indicating whether the passwords match
        """
        if password and self.password:
            stored_password = self.password.encode('utf-8')
            password = password.encode('utf-8')
            success = bcrypt.checkpw(password, stored_password)
            if success:
                self._logger.info(f"{self._method_path()}: {success}")
            else:
                self._logger.warning(f"{self._method_path()}: {success}")
            return success
        else:
            self._logger.warning(f"{self._method_path()}: password is null")
            return False
    
    def populate(self, **kwargs):
        """
        Populates the User object attributes with provided values.

        Parameters:
        - kwargs: Keyword arguments containing attribute-value pairs
        """
        try:
            for k, v in kwargs.items():
                if v:
                    if k == 'password':
                        v = self._hash_password(v)
                    setattr(self, k, v)
            self._logger.info(f"{self._method_path()}: {True}")
        except Exception as e:
            self._logger.warning(f"{self._method_path()}: {e}")

    def clear(self):
        """
        Clears all attributes of the User object.
        """
        for k in self.__dict__.keys():
            setattr(self, k, None)
        self._logger.info(f"{self._method_path()}: complete")

    def push(self):
        """
        Pushes the User object data into the database.
        
        Returns:
        - success: Boolean indicating whether the operation was successful
        """
        columns = ['user_id', 'username', 'password']
        values  = [ '?', '?' ]
        params  = [self.username, self.username, self.password]
        for key, value in self.__dict__.items():
            if key not in columns:
                columns.append(key)
                params.append(value)
                values.append('?')
        success, result = self._db.execute(f'INSERT OR REPLACE INTO Users ( {','.join(columns)} ) VALUES ( (SELECT user_id FROM Users WHERE username = ?),{','.join(values)} )', params)
        if success: 
            self._logger.info(f"{self._method_path()}: complete")
        else: 
            self._logger.info(f"{self._method_path()}: {result}")
        return success

    def find(self):
        """
        Finds a user in the database by username.

        Returns:
        - found: Boolean indicating whether the user was found
        """
        success, result = self._db.execute("SELECT * FROM Users WHERE username = ?", (self.username,))
        if success:
            user_data = result.fetchone()
            if user_data:
                self._logger.info(f"{self._method_path()}['{self.username}']: {True}")
                for column_name, value in user_data.items():
                    setattr(self, column_name, value)
            else:
                self._logger.warning(f"{self._method_path()}['{self.username}']: {False}")
        else:
            self._logger.error(f"{self._method_path()}['{self.username}']: {result}")
        return bool(self.user_id)

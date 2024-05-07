import bcrypt
import inspect
from models.logger import logger
from models.database import db

class User:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.password = None

    @classmethod
    def _method_path(cls):
        return "{0}.{1}".format(cls.__name__, inspect.stack()[1][3])
    
    def db_start(self):
        status, result = db.execute('''
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
        if status:
            logger.info(f"{self._method_path()}: {status}")
        else:
            logger.error(f"{self._method_path()}: {result}")
            exit()

    @classmethod
    def _hash_password(cls, password:str):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
    
    def hash_password(self, password:str):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

    def validate(self, password:str ):
        if password and self.password:
            stored_password = self.password.encode('utf-8')
            password = password.encode('utf-8')
            success = bcrypt.checkpw(password, stored_password)
            if success:
                logger.info(f"{self._method_path()}: {success}")
            else:
                logger.warning(f"{self._method_path()}: {success}")
            return success
        else:
            logger.warning(f"{self._method_path()}: password is null")
            return False
    
    # def populate(self, **kwargs):
    #     try:
    #         for k, v in kwargs.items():
    #             if v:
    #                 if k == 'password':
    #                     v = self._hash_password(v)
    #                 setattr(self, k, v)
    #         logger.info(f"{self._method_path()}: {True}")
    #     except Exception as e:
    #         logger.warning(f"{self._method_path()}: {e}")

    def clear(self):
        for k in self.__dict__.keys():
            setattr(self, k, None)
        logger.info(f"{self._method_path()}: complete")

    def push(self):
        columns = ['user_id', 'username', 'password']
        values  = [ '?', '?' ]
        params  = [self.username, self.username, self.password]
        for key, value in self.__dict__.items():
            if key not in columns:
                columns.append(key)
                params.append(value)
                values.append('?')
        success, result = db.execute(f'INSERT OR REPLACE INTO Users ( {','.join(columns)} ) VALUES ( (SELECT user_id FROM Users WHERE username = ?),{','.join(values)} )', params)
        if success: 
            logger.info(f"{self._method_path()}: complete")
        else: 
            logger.info(f"{self._method_path()}: {result}")
        return success

    def update_by_user_id(self, user_id, **kwargs):
        try:
            values  = []
            params  = []
            for k, v in kwargs.items():
                if v:
                    values.append(f'{k}=?')
                    params.append(v)
            params.append(user_id)
            status, result = db.execute(f'UPDATE Users SET {' AND '.join(values)} WHERE user_id=?', params)
            if status:
                logger.info(f"{self._method_path()}: {status}")
                return status, result.fetchone()
            else: 
                logger.warning(f"{self._method_path()}: {result}")
                return False, result
        except Exception as err:
            logger.error(f'''{self._method_path()}: {err}''')
            return False, None


    def find_by_username(self, username):
        try:
            status, result = db.execute(f'SELECT * FROM Users WHERE username=?', (username,))
            if status:
                logger.info(f'''{self._method_path()}: {status}''')
                return status, result.fetchone()
            logger.warning(f'''{self._method_path()}: {result}''')
            return False, result
        except Exception as err:
            logger.error(f'''{self._method_path()}: {err}''')
        return False, None
    

    def populate(self, **kwargs):
        try:
            for k, v in kwargs.items():
                if v: setattr(self, k, v)
            logger.info(f"{self._method_path()}: {True}")
        except Exception as err:
            logger.warning(f"{self._method_path()}: {err}")

    def validate_password(self, incoming_password:str ):
        try:
            stored_password = self.password.encode('utf-8')
            incoming_password = incoming_password.encode('utf-8')
            status = bcrypt.checkpw(incoming_password, stored_password)
            if status:
                logger.info(f"{self._method_path()}: {status}")
            else:
                logger.warning(f"{self._method_path()}: {status}")
            return status
        except Exception as err:
            logger.warning(f"{self._method_path()}: {err}")
        return None
    
    # def find(self):
    #     success, result = db.execute("SELECT * FROM Users WHERE username = ?", (self.username,))
    #     if success:
    #         user_data = result.fetchone()
    #         if user_data:
    #             logger.info(f"{self._method_path()}['{self.username}']: {True}")
    #             for column_name, value in user_data.items():
    #                 setattr(self, column_name, value)
    #         else:
    #             logger.warning(f"{self._method_path()}['{self.username}']: {False}")
    #     else:
    #         logger.error(f"{self._method_path()}['{self.username}']: {result}")
    #     return bool(self.user_id)

user = User()

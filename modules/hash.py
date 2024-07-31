import bcrypt
from modules.logger import logger, method_path

def hash_password(password:str):
    logger.info(f"{method_path()}: hash_password")
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")

def validate_passwords(password:str, db_password:str):
    try:
        if password and db_password:
            stored_password = db_password.encode('utf-8')
            password = password.encode('utf-8')
            status = bcrypt.checkpw(password, stored_password)
            if status:
                logger.info(f"{method_path()}: {status}")
            else:
                logger.warning(f"{method_path()}: {status}")
            return status
        else:
            logger.warning(f"{__name__}: password is null")
            return False
    except Exception as err:
        logger.error(f"{__name__}: {err}")
        return False
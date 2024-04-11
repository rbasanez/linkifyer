import logging
import sqlite3
from pathlib import Path
from datetime import datetime

current_path = Path(__file__).resolve().parent

# start logger
log_name = '%s_%s.log' % ('update', datetime.today().strftime('%Y-%m-%d'))
log_path = current_path / 'logs'
log_path.mkdir(parents=True, exist_ok=True)
log_path = log_path / log_name
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s [%(threadName)-12.12s] [%(levelname)-7.7s]  %(message)s',
    handlers = [
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('update')

# connect to db
db_path = current_path / f'database.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
conn.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
cursor = conn.cursor()

def add_column_if_not_exists(db, table_name, column_name, column_definition):
    try:
        result = db.execute(f'PRAGMA table_info({table_name})')
        columns = result.fetchall()
        column_names = [column['name'] for column in columns]
        if column_name not in column_names:
            result = db.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}')
            logger.info( f'updated:{result.rowcount}' )
    except Exception as err:
        logger.error(err)
        exit()

# Add columns if they do not exist
logger.info('update db column: @Items:favorite')
add_column_if_not_exists(cursor, 'Items' ,'favorite', 'INT DEFAULT 0')

logger.info('update success!')

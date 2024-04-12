import logging
from datetime import datetime
from pathlib import Path

log_name = '%s_%s.log' % ('app', datetime.today().strftime('%Y-%m-%d'))
log_path = Path(__file__).resolve().parent.parent / "logs"
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

logger = logging.getLogger('main_app')
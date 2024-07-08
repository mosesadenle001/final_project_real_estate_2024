import logging
from logging.handlers import RotatingFileHandler
import os

file_handler = RotatingFileHandler('logs/real_estate.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.info('Real Estate Listings Platform startup')

if not os.path.exists('logs'):
    os.mkdir('logs')
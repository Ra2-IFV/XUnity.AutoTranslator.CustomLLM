import logging

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s L%(lineno)d %(message)s')
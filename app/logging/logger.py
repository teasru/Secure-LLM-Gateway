import logging
import json

logger = logging.getLogger("gateway")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_event(event: dict):
    logger.info(json.dumps(event))

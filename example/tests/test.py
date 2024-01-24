import json
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setUpRun(data, step):
    logger.debug(f"Data: {json.dumps(data)}")
    logger.debug(f"Step: {json.dumps(step)}")


def tearDownRun(data, step):
    logger.debug(f"Data: {json.dumps(data)}")
    logger.debug(f"Step: {json.dumps(step)}")


def beforeStep(data, step):
    logger.debug(f"Data: {json.dumps(data)}")
    logger.debug(f"Step: {json.dumps(step)}")


def afterStep(data, step):
    logger.debug(f"Data: {json.dumps(data)}")
    logger.debug(f"Step: {json.dumps(step)}")


class ModelName:

    def vertex_A(self, data, step):
        logger.debug(f"Data: {json.dumps(data)}")
        logger.debug(f"Step: {json.dumps(step)}")

    def vertex_B(self, data, step):
        logger.debug(f"Data: {json.dumps(data)}")
        logger.debug(f"Step: {json.dumps(step)}")

    def edge_A(self, data, step):
        logger.debug(f"Data: {json.dumps(data)}")
        logger.debug(f"Step: {json.dumps(step)}")

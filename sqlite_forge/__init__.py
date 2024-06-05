import logging
import os

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = os.path.dirname(MODULE_PATH)

DATABASE_PATH = f"{REPO_PATH}"


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Get the root logger
log = logging.getLogger()

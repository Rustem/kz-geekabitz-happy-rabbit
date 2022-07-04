import logging
import os, django

# TODO setup generic django logging
import sys

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream = sys.stdout,
                    filemode = "w",
                    format = LOG_FORMAT,
                    level = logging.INFO)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyrabbit.settings')
django.setup()

from tgbot.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()
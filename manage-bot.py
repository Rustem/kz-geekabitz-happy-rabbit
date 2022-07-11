import sys
import logging

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout,
                    filemode="w",
                    format=LOG_FORMAT,
                    level=logging.INFO)

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyrabbit.settings')
django.setup()

from django.conf import settings

# TODO setup generic django logging

if settings.TELEGRAM_TOKEN is None:
    logging.error(
        "Please provide TELEGRAM_TOKEN in .env file.\n"
        "Example of .env file: https://github.com/Rustem/kz-geekabitz-happy-rabbit/blob/main/.env_example"
    )
    sys.exit(1)

if __name__ == "__main__":
    try:
        from tgbot.core.happy_rabbit import HappyRabbitBot
        hr_bot = HappyRabbitBot(settings.TELEGRAM_TOKEN)
        hr_bot.run()
    except Exception as e:
        logging.critical("Could not start bot: {}.".format(repr(e)))
        raise

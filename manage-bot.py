import sys
import logging
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happyrabbit.settings')
django.setup()

from tgbot.service.external_account import TelegramUserService
from tgbot.service.auth import AuthService
from tgbot.application import HappyRabbitApplication

LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout,
                    filemode="w",
                    format=LOG_FORMAT,
                    level=logging.INFO)

from django.conf import settings

# TODO setup generic django logging

if settings.TELEGRAM_TOKEN is None:
    logging.error(
        "Please provide TELEGRAM_TOKEN in .env file.\n"
        "Example of .env file: https://github.com/Rustem/kz-geekabitz-happy-rabbit/blob/main/.env_example"
    )
    sys.exit(1)


def initialize_application():
    auth_service = AuthService()
    external_user_service = TelegramUserService()
    return HappyRabbitApplication(auth_service, external_user_service)


if __name__ == "__main__":
    try:
        from tgbot.core.happy_rabbit import HappyRabbitBot
        happy_rabbit_app = initialize_application()
        hr_bot = HappyRabbitBot(happy_rabbit_app, settings.TELEGRAM_TOKEN)
        hr_bot.run()
    except Exception as e:
        logging.critical("Could not start bot: {}.".format(repr(e)))
        raise

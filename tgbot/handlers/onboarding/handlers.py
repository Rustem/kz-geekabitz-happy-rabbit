import logging

from telegram import Update
from telegram.ext import CallbackContext

from happyrabbit.abc.external_account import ExternalAccount
from . import static_text
from .keyboards import make_keyboard_for_start_command
from ...backends import TelegramUserBackend

logger = logging.getLogger(__name__)

telegram_user_backend = TelegramUserBackend()


def account_display(account: ExternalAccount) -> str:
    return f'{account.get_external_user_id()}:{account.get_username()}'


def chat_display(chat):
    return f'chat:{chat.id}'


def command_start(update: Update, context: CallbackContext) -> None:
    external_account = telegram_user_backend.extract_external_account(update)
    external_profile = external_account.get_external_profile()
    # TODO get or create an account
    # TODO add new chat session
    message = '/{cmdname} command was issued by {user} in {chat}'
    logger.info(message.format(
        cmdname='start',
        user=account_display(external_account),
        chat=chat_display(update.message.chat)))
    # transform to Account object

    text = static_text.start_created.format(first_name=external_profile.get_first_name())
    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())

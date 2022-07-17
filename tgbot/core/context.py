from typing import List

from telegram import Update, Bot
from telegram.message import Message

from happyrabbit.abc.external_account import ExternalSession, ExternalAccount
from tgbot.service.external_account import TelegramUserService


class ConversationContext:
    bot: Bot = None

    update: Update = None

    args: List[str] = None

    session: ExternalSession

    def __init__(self, bot: Bot, update: Update, args: List[str]=None):
        self.session = None
        self.bot = bot
        self.update = update
        self.args = args or []

    @property
    def message(self) -> Message:
        return self.update.message

    @property
    def chat_id(self):
        return self.message.chat_id

    @property
    def text(self):
        return self.message.text

    @property
    def reply_to(self):
        if self.message.chat.type != 'private':
            return self.message.message_id
        else:
            return None

    @property
    def external_user_id(self) -> int:
        # TODO this should be either injected on creation or converted using a provider
        user_data = TelegramUserService.extract_user_data(self.update)
        return user_data['id']

    def set_session(self, session: ExternalSession):
        self.session = session


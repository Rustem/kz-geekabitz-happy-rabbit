from typing import List, Optional, Any

from telegram import Update, Bot, CallbackQuery
from telegram.ext import CallbackContext
from telegram.message import Message

from happyrabbit.abc.errors import IllegalStateError
from happyrabbit.abc.external_account import ExternalSession, ExternalAccount
from tgbot.service.external_account import TelegramUserService


class ConversationContext:
    bot: Bot = None

    update: Update = None

    args: List[str] = None

    session: ExternalSession

    callback_context: CallbackContext

    def __init__(self, bot: Bot, update: Update, callback_context: CallbackContext):
        self.session = None
        self.bot = bot
        self.update = update
        self.args = callback_context.args or []
        self.callback_context = callback_context

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

    def user_display(self):
        account = self.session.get_account()
        return "{}:{}".format(account.get_external_user_id(), account.get_username())

    def set_session(self, session: ExternalSession):
        self.session = session

    def get_session(self) -> ExternalSession:
        return getattr(self, 'session', None)

    @property
    def callback_query(self) -> Optional[CallbackQuery]:
        return self.update.callback_query

    def drop_callback_data(self):
        if self.callback_query is not None:
            self.callback_context.drop_callback_data(self.callback_query)

    def update_user_data(self, key: str, value: Any):
        if self.callback_context.user_data is None:
            raise IllegalStateError("Cannot store user specific data as command handler is not configured.")
        self.callback_context.user_data[key] = value

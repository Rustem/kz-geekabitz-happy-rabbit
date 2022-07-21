import logging
from abc import ABC, abstractmethod
from typing import Dict, Type, Callable, List

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.callbackcontext import CC, CallbackContext
from telegram.ext.utils.types import CCT

from tgbot.core.context import ConversationContext
from tgbot.core.decorators import command_handler
from tgbot.core.dialogs.base import Dialog
from tgbot.core.message_sender import MessageSender

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    telegram_token: str = None

    bot: Bot = None

    dialogs: Dict[Type[int], Type[Dialog]]

    updater: Updater

    message_sender: MessageSender

    def __init__(self, telegram_token: str):
        self.bot = Bot(token=telegram_token)
        self.telegram_token = telegram_token
        self.updater = Updater(bot=self.bot)
        self.dispatcher = self.updater.dispatcher
        self.message_sender = MessageSender(self.bot)
        self.dialogs = {}

    @command_handler(description="To cancel current conversation")
    def cmd_cancel(self, context: ConversationContext):
        try:
            dialog = self.dialogs[context.chat_id]
            if dialog.cancel(context):
                del self.dialogs[context.chat_id]
        except KeyError:
            pass

    def _error_handler(self, update: Update, error_context: CC):
        raise error_context.error

    def _wrap_cmd(self, handler) -> Callable[[Type[Bot], Type[Update], Type[CallbackContext]], None]:

        def wrapper(update: Update, callback_context: CallbackContext):
            context = ConversationContext(self.bot, update, callback_context.args)
            context = self.wrap_context(context)
            handler(context)

        return wrapper

    def _msg_handler(self, update: Update, cct: CCT):
        context = ConversationContext(self.bot, update)
        context = self.wrap_context(context)

        if context.chat_id in self.dialogs:
            dialog = self.dialogs[context.chat_id]

            if dialog.advance_next(context):
                del self.dialogs[context.chat_id]

            return

        if context.text is not None and context.text.startswith('/'):
            # command with such name does not exist
            self.command_not_found(context)

    def run(self):
        for key in dir(self):
            # TODO instead verify that callable is decorated with @command_handler
            if not key.startswith('cmd_'):
                continue

            cmd_name = key[4:]
            handler = self._wrap_cmd(getattr(self, key))

            self.dispatcher.add_handler(
                CommandHandler(cmd_name, handler, pass_args=True))

        self.dispatcher.add_error_handler(self._error_handler)
        self.dispatcher.add_handler(
            MessageHandler(Filters.text, self._msg_handler))

        self.updater.start_polling()
        self.updater.idle()

    @abstractmethod
    def wrap_context(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

    @abstractmethod
    def command_not_found(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

import logging
import os.path
from abc import ABC, abstractmethod
from typing import Dict, Type, Callable, List

from telegram import Bot, Update
from telegram.bot import RT
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence, \
    CallbackQueryHandler, InvalidCallbackData, ConversationHandler
from telegram.ext.callbackcontext import CC, CallbackContext
from telegram.ext.utils.types import CCT
from tgbot.core.callback_handlers import TgInlineCallbackHandler
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

    inline_callback_handler: TgInlineCallbackHandler

    def __init__(self, telegram_token: str):
        self.telegram_token = telegram_token
        cur_path = os.path.abspath(os.path.dirname(__file__))
        logger.info("Create file at " + cur_path + '/' + 'aaa.pickle')
        persistence = PicklePersistence(
            filename=cur_path + '/' + 'aaa.pickle', store_callback_data=True
        )
        self.updater = Updater(token=telegram_token, persistence=persistence, arbitrary_callback_data=True)
        self.bot = self.updater.bot
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

    def _wrap_cmd(self, handler) -> Callable[[Update, CCT], RT]:

        def wrapper(update: Update, callback_context: CallbackContext) -> RT:
            context = ConversationContext(self.bot, update, callback_context)
            context = self.wrap_context(context)
            return handler(context)

        wrapper.__name__ = "wrapped (" + handler.__name__ + ")"
        return wrapper

    def _msg_handler(self, update: Update, cct: CCT):
        context = ConversationContext(self.bot, update, cct)
        context = self.wrap_context(context)

        if context.chat_id in self.dialogs:
            dialog = self.dialogs[context.chat_id]

            if dialog.advance_next(context):
                del self.dialogs[context.chat_id]

            return

        if context.text is not None and context.text.startswith('/'):
            # command with such name does not exist
            self.command_not_found(context)

        logger.warning("Unrecognized text from user: [%s]", context.text)

    def start_dialog(self, context: ConversationContext, dialog: Dialog):
        # TODO log
        self.dialogs[context.chat_id] = dialog
        dialog.execute_current_turn(context)

    def handle_invalid_button(self, update: Update, context: CallbackContext) -> None:
        """Informs the user that the button is no longer available."""
        update.callback_query.answer()
        update.effective_message.edit_text(
            'Sorry, I could not process this button click 😕 Please send /start to get a new keyboard.'
        )
        logger.error("Invalid keyboard or button")

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
        self.dispatcher.add_handler(CallbackQueryHandler(self._wrap_cmd(self.callback_query_handler)))
        self.dispatcher.add_handler(
            CallbackQueryHandler(self.handle_invalid_button, pattern=InvalidCallbackData)
        )
        for conv_handler in self.add_conversation_handlers():
            self.dispatcher.add_handler(conv_handler)
        self.updater.start_polling()
        self.updater.idle()

    @abstractmethod
    def add_conversation_handlers(self) -> List[ConversationHandler]:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def callback_query_handler(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

    @abstractmethod
    def wrap_context(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

    @abstractmethod
    def command_not_found(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

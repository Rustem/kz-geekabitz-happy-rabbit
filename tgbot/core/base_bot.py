import logging
import os.path
from abc import ABC, abstractmethod
from typing import Dict, Type, Callable, Optional

from telegram import Bot, Update, CallbackQuery, ReplyMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence, \
    CallbackQueryHandler, InvalidCallbackData
from telegram.ext.callbackcontext import CC, CallbackContext
from telegram.ext.utils.types import CCT
from telegram.utils.types import JSONDict

from happyrabbit.abc.errors import IllegalStateError
from happyrabbit.abc.service.activity import NextPageRequest
from tgbot.core.context import ConversationContext
from tgbot.core.decorators import command_handler, get_inline_callback_handler, callback_handler_registry
from tgbot.core.dialogs.base import Dialog
from tgbot.core.message_sender import MessageSender

logger = logging.getLogger(__name__)


class ExtraParamContainer:

    callback_handler: str

    @staticmethod
    def from_dict(extra_params: JSONDict):
        return ExtraParamContainer(**extra_params)

    def __init__(self, callback_handler:str =None):
        self.callback_handler = callback_handler

    def get_callback_handler(self) -> Callable:
        return get_inline_callback_handler(self.callback_handler)


class CallbackResult:
    text: str
    reply_markup: Optional[ReplyMarkup]

    def __init__(self, text, reply_markup: Optional[ReplyMarkup]=None):
        self.text = text
        self.reply_markup = reply_markup

    def to_dict(self) -> JSONDict:
        return dict(**self.__dict__)


class BaseBot(ABC):
    telegram_token: str = None

    bot: Bot = None

    dialogs: Dict[Type[int], Type[Dialog]]

    updater: Updater

    message_sender: MessageSender

    def __init__(self, telegram_token: str):
        self.telegram_token = telegram_token
        cur_path = os.path.abspath(os.path.dirname(__file__))
        print("Create file at " + cur_path + '/' + 'aaa.pickle')
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

    def _wrap_cmd(self, handler) -> Callable[[Type[Bot], Type[Update], Type[CallbackContext]], None]:

        def wrapper(update: Update, callback_context: CallbackContext):
            context = ConversationContext(self.bot, update, callback_context.args)
            context = self.wrap_context(context)
            return handler(context)

        wrapper.__name__ = "wrapped (" + handler.__name__ + ")"
        return wrapper

    def _wrap_cb(self, handler) -> Callable[[Type[Bot], Type[Update], Type[CallbackContext]], None]:

        def wrapper(update: Update, callback_context: CallbackContext):
            context = ConversationContext(self.bot, update, callback_context.args)
            context = self.wrap_context(context)
            return handler(self, context)

        wrapper.__name__ = "wrapped (" + handler.__name__ + ")"
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

    def callback_data_handler(self, update: Update, context: CallbackContext):
        page_request = self.decode_callback_data(update.callback_query)
        if not page_request:
            print("warn: no callback data to parse")
            return

        print("decoded", page_request.to_dict())
        # TODO get callback_handler
        # TODO  execute callback_handler Result(text, reply_markup,
        # TODO  if result is not none -> edit text response
        extra_param_container = ExtraParamContainer.from_dict(page_request.extra_params)
        callback_handler = extra_param_container.get_callback_handler()

        print(f'Executing callback handler: {callback_handler}')

        context.args = [page_request]
        callback_result = callback_handler(update, context)
        print("Reply with: ", callback_result.to_dict())
        update.callback_query.edit_message_text(**callback_result.to_dict())

        # we can delete the data stored for the query, because we've replaced the buttons
        context.drop_callback_data(update.callback_query)

    def handle_invalid_button(self, update: Update, context: CallbackContext) -> None:
        """Informs the user that the button is no longer available."""
        update.callback_query.answer()
        update.effective_message.edit_text(
            'Sorry, I could not process this button click 😕 Please send /start to get a new keyboard.'
        )
        print("invalid button")

    def run(self):
        for key in callback_handler_registry:
            callback_handler_registry[key] = self._wrap_cb(callback_handler_registry[key])

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
        self.dispatcher.add_handler(CallbackQueryHandler(self.callback_data_handler))
        self.dispatcher.add_handler(
            CallbackQueryHandler(self.handle_invalid_button, pattern=InvalidCallbackData)
        )
        self.updater.start_polling()
        self.updater.idle()

    @abstractmethod
    def wrap_context(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

    @abstractmethod
    def command_not_found(self, context: ConversationContext):
        raise NotImplementedError("not implemented")

    def decode_callback_data(self, callback_query: CallbackQuery) -> Optional[NextPageRequest]:
        callback_query.answer()
        encoded_callback_data = callback_query.data
        if not encoded_callback_data:
            return None
        try:
            return NextPageRequest.base64_decode(encoded_callback_data)
        except RuntimeError as e:
            raise IllegalStateError("unable to decode callback data", e)
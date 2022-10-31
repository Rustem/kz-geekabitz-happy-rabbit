import logging
from typing import Optional, Tuple

from telegram import CallbackQuery

from happyrabbit.abc.errors import IllegalStateError
from .base import CallbackHandler, CallbackResult, Event, Response
from .pagination import PaginationEvent, PaginationCallbackHandler
from .types import CBH
from ..context import ConversationContext

logger = logging.getLogger(__name__)


class TgInlineCallbackHandler:
    callback_handlers: Tuple[CBH]

    def __init__(self, callback_handlers: Tuple[CBH]):
        self.callback_handlers = callback_handlers

    def handle(self, context: ConversationContext):
        if context.callback_query is None:
            logger.warning("No callback_query provided, skipping execution")
            return None

        event = self.decode_callback_data(context.callback_query)

        callback_result: CallbackResult = None
        for handler in self.callback_handlers:
            logger.info("Trying next callback handler: %s", type(handler).__name__)
            if handler.can_handle(event, context):
                logger.info("Found callback handler: %s", type(handler).__name__)
                coerced_event = handler.coerce_event(event)
                callback_result = handler.handle(coerced_event, context)
                break

        if callback_result is None:
            logger.warn("No callback handler found for event: %s", event.name)
            return

        if not callback_result.is_ok():
            raise callback_result.error # rethrow

        success = callback_result.result.to_dict()
        logger.info("Callback handler replied with: %s", success)
        context.callback_query.edit_message_text(**success)

        # we can delete the data stored for the query, because we've replaced the buttons
        context.drop_callback_data()
        if callback_result.next_state is not None:
            return callback_result.next_state

    @staticmethod
    def decode_callback_data(callback_query: CallbackQuery) -> Optional[Event]:
        callback_query.answer()
        event = callback_query.data
        if not event:
            return None
        if not isinstance(event, Event):
            raise IllegalStateError("improperly configured callback data")
        return event

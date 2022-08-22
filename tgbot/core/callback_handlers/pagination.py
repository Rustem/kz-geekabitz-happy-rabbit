from typing import Type

from telegram.utils.types import JSONDict

from happyrabbit.abc.service.activity import NextPageRequest
from tgbot.application import HappyRabbitApplication
from tgbot.core import messages
from tgbot.core.callback_handlers.base import CallbackHandler, Event, CallbackResult
from tgbot.core.context import ConversationContext
from tgbot.core.formatters.activity import inline_activity_list
from tgbot.core.markup.pagination import PaginationKeyboardMarkup


class PaginationEvent(Event):

    EVENT_NAME = "activity_pagination"

    def parse_payload(self) -> NextPageRequest:
        if self.payload is None:
            raise TypeError("event payload must be non-empty string")
        return NextPageRequest.base64_decode(self.payload)

    @staticmethod
    def get_event_name() -> str:
        return PaginationEvent.EVENT_NAME


class PaginationCallbackHandler(CallbackHandler):

    happy_rabbit_app: HappyRabbitApplication

    def __init__(self, happy_rabbit_app: HappyRabbitApplication):
        self.happy_rabbit_app = happy_rabbit_app

    @property
    def event_class(self) -> Type[Event]:
        # EVT = TypeVar('EVT', bound='Event')
        # TODO restrict with TypeVar()
        return PaginationEvent

    @property
    def event_name(self) -> str:
        return PaginationEvent.EVENT_NAME

    def can_handle(self, event: Event, context: ConversationContext) -> bool:
        return self.event_name == event.name

    def handle(self, event: PaginationEvent, context: ConversationContext) -> CallbackResult:
        # TODO add error handling mechanism CallbackResult.error()
        page_request = event.parse_payload()
        activities_page = self.happy_rabbit_app.load_next_page_of_activities(context.session, page_request)

        reply_markup = PaginationKeyboardMarkup(activities_page.total_pages,
                                                activities_page.pagination_token,
                                                activities_page.page_number,
                                                callback_data_provider=PaginationEvent.create)
        inline_activities = inline_activity_list(activities_page.page_number, activities_page.items)
        return CallbackResult.success(
            text=messages.SHOW_ACTIVITIES_OK.format(inline_activities=inline_activities),
            reply_markup=reply_markup.to_markup())

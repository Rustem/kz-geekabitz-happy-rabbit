from abc import ABC, abstractmethod
from typing import Optional, Type

from telegram import ReplyMarkup
from telegram.utils.types import JSONDict

from happyrabbit.abc.errors import IllegalArgumentError
from tgbot.core.context import ConversationContext


class Event(ABC):
    name: str
    payload: str

    @classmethod
    def create(cls, payload):
        return cls(cls.get_event_name(), payload)

    def __init__(self, name, payload):
        self.name = name
        self.payload = payload

    @staticmethod
    @abstractmethod
    def get_event_name() -> str:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def parse_payload(self):
        raise NotImplementedError("not implemented")

    def to_dict(self):
        return dict(self.__dict__)


class Response(ABC):

    def to_dict(self) -> JSONDict:
        return dict(**self.__dict__)


class OkResponse(Response):
    text: str
    reply_markup: Optional[ReplyMarkup]

    def __init__(self, text, reply_markup: Optional[ReplyMarkup] = None):
        self.text = text
        self.reply_markup = reply_markup


class ErrorResponse(Response):
    error: BaseException
    error_code: int

    def __init__(self, error: BaseException, error_code: int):
        self.error = error
        self.error_code = error_code


class CallbackResult:
    success: bool
    error: Optional[ErrorResponse]
    result: Optional[OkResponse]

    @staticmethod
    def success(text, reply_markup):
        ok = OkResponse(text, reply_markup)
        return CallbackResult(True, error=None, result=ok)

    @staticmethod
    def error(cause: BaseException, error_code=400):
        bad = ErrorResponse(cause, error_code)
        return CallbackResult(False, error=bad, result=None)

    def __init__(self, success: bool, error: Optional[ErrorResponse] = None, result: Optional[OkResponse] = None):
        if success and error:
            raise IllegalArgumentError("Result is successful, but ErrorResponse is not null")
        if not success and result:
            raise IllegalArgumentError("Result is unsuccessful, but OkResponse is not null")
        self.success = success
        self.error = error
        self.result = result

    def to_dict(self) -> JSONDict:
        return {
            'success': self.success,
            'error': self.error.to_dict() if self.error else None,
            'result': self.result.to_dict() if self.result else None
        }

    def is_ok(self) -> bool:
        return self.success is True


class CallbackHandler(ABC):

    def coerce_event(self, event: Event) -> Event:
        return self.event_class(**event.to_dict())

    @property
    @abstractmethod
    def event_class(self) -> Type[Event]:
        raise NotImplementedError("not implemented")

    @property
    @abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def can_handle(self, event: Event, context: ConversationContext) -> bool:
        raise NotImplementedError("not implemented error")

    @abstractmethod
    def handle(self, event: Event, context: ConversationContext) -> CallbackResult:
        raise NotImplementedError("not implemented error")

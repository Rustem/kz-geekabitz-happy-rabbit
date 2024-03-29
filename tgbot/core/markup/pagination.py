from typing import List, Optional, Callable

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.utils.types import JSONDict

from happyrabbit.abc.service.activity import NextPageRequest
from tgbot.core.callback_handlers import Event


class PaginationKeyboardMarkup:
    first_page_label = '« {}'
    previous_page_label = '‹ {}'
    next_page_label = '{} ›'
    last_page_label = '{} »'
    current_page_label = '·{}·'

    page_count: int
    pagination_token: str
    page_number: int
    callback_data_provider: Callable[[str], Event]

    def __init__(self, page_count: int, pagination_token: str, page_number: int = 1,
                 callback_data_provider: Callable[[str], Event] = None):
        if not page_number:
            page_number = 1
        if page_number > page_count:
            page_number = page_count
        self.page_number = page_number
        self.page_count = page_count
        self.pagination_token = pagination_token
        self.callback_data_provider = callback_data_provider

    def to_markup(self) -> InlineKeyboardMarkup:
        return self.build_keyboard_control()

    def build_keyboard_control(self) -> InlineKeyboardMarkup:
        pagination_keyboard = self.build_keyboard()
        return InlineKeyboardMarkup.from_row(pagination_keyboard)

    def build_keyboard(self) -> List[InlineKeyboardButton]:
        if self.page_count == 1:
            return []

        elif self.page_count <= 5:
            keyboard = []
            for page in range(1, self.page_count + 1):
                keyboard.append(self.btn(page))
            return keyboard

        else:
            return self._build_keyboard_for_multi_pages()

    def _build_keyboard_for_multi_pages(self) -> List[InlineKeyboardButton]:
        if self.page_number <= 3:
            return self._build_start_keyboard()

        elif self.page_number > self.page_count - 3:
            return self._build_finish_keyboard()

        else:
            return self._build_middle_keyboard()

    def _build_start_keyboard(self) -> List[InlineKeyboardButton]:
        keyboard = []
        for page in range(1, 4):
            keyboard.append(self.btn(page))
        keyboard.append(self.btn(4, next=True))
        keyboard.append(self.btn(self.page_count, last=True))
        return keyboard

    def _build_finish_keyboard(self) -> List[InlineKeyboardButton]:
        keyboard = [self.btn(1, first=True),
                    self.btn(self.page_count - 3, previous=True)]

        for page in range(self.page_count - 2, self.page_count + 1):
            keyboard.append(self.btn(page))

        return keyboard

    def _build_middle_keyboard(self) -> List[InlineKeyboardButton]:
        keyboard = [self.btn(1, first=True), self.btn(self.page_number - 1, previous=True),
                    self.btn(self.page_number), self.btn(self.page_number + 1, next=True),
                    self.btn(self.page_count, last=True)]

        return keyboard

    def btn(self, num, first=None, previous=None, next=None, last=None):
        text = str(num)
        if first:
            text = self.first_page_label.format(text)
        elif previous:
            text = self.previous_page_label.format(text)
        elif next:
            text = self.next_page_label.format(text)
        elif last:
            text = self.last_page_label.format(text)

        page_request = NextPageRequest(self.pagination_token, num)
        callback_data = self.callback_data_provider(NextPageRequest.base64_encode(page_request))
        return InlineKeyboardButton(text, callback_data=callback_data)

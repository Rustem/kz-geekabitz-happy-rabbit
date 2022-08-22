import base64
import datetime
import json
from abc import ABC, abstractmethod
from typing import List

from django.conf import settings
from telegram.utils.types import JSONDict

from happyrabbit.abc.activity import Activity

DEFAULT_PAGE_SIZE = getattr(settings, 'ACTIVITY_SEARCH_PAGE_SIZE', 500)


class SearchQuery:
    owner_id: int
    category_name: str
    include_orphaned: bool

    # sort order of the search results: '-pub_date', 'headline',
    order_by: List[str]
    # TODO offset
    # TODO limit

    def __init__(self, owner_id: int, category_name: str, include_orphaned: bool = False, order_by: List[str] = None):
        self.owner_id = owner_id
        self.category_name = category_name
        self.include_orphaned = include_orphaned
        self.order_by = order_by if order_by is not None else list()


class NextPageRequest:
    pagination_token: str
    page: int
    extra_params: JSONDict

    def __init__(self, pagination_token: str, page: int, extra_params: JSONDict=None):
        self.pagination_token = pagination_token
        self.page = page
        self.extra_params = extra_params or {}

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def base64_encode(page_request) -> str:
        params = page_request.to_dict()
        payload = json.dumps(params).encode()
        return base64.urlsafe_b64encode(payload).decode()

    @staticmethod
    def base64_decode(encoded_payload: str):
        decoded_payload = base64.urlsafe_b64decode(encoded_payload.encode())
        params = json.loads(decoded_payload)
        return NextPageRequest(**params)


class Pagination:

    @abstractmethod
    def get_pagination_token(self) -> str:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_min_index(self) -> int:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_max_index(self) -> int:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_query(self) -> SearchQuery:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_page_size(self) -> int:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_created_at(self) -> datetime.datetime:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_expire_at(self) -> datetime.datetime:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_owner_id(self) -> int:
        raise NotImplementedError("not implemented")


class PaginatedResponse:
    items: List[Activity]
    count: int
    pagination_token: str
    page_number: int
    total_pages: int
    next: NextPageRequest
    previous: NextPageRequest

    def __init__(self, items: List[Activity], count: int, pagination_token: str, page_number: int,
                 total_pages: int, next: NextPageRequest = None, previous: NextPageRequest = None):
        self.items = items
        self.count = count
        self.total_pages = total_pages
        self.pagination_token = pagination_token
        self.page_number = page_number
        self.next = next
        self.previous = previous


class ActivitySearchService(ABC):

    @abstractmethod
    def search(self, search_query: SearchQuery) -> List[Activity]:
        """
        @param {SearchQuery} search query
        @returns {List[Activity]} results
        """
        # TODO implement pagination (P1)
        raise NotImplementedError("not implemented")

    @abstractmethod
    def search_paginated(self, search_query: SearchQuery) -> PaginatedResponse:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def load_next_page(self, page_request: NextPageRequest) -> PaginatedResponse:
        raise NotImplementedError("not implemented")

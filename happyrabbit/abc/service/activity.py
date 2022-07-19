from abc import ABC, abstractmethod
from typing import List

from django.conf import settings

from happyrabbit.abc.activity import Activity

DEFAULT_PAGE_SIZE = getattr(settings, 'ACTIVITY_SEARCH_PAGE_SIZE', 500)


class SearchQuery:
    owner_id: int
    category_name: str
    include_orphaned: bool

    # sort order of the search results: '-pub_date', 'headline',
    order_by: List[str]
    page_size: int

    def __init__(self, owner_id: int, category_name: str, include_orphaned: bool = False, order_by: List[str] = None, page_size: int = 0):
        self.owner_id = owner_id
        self.category_name = category_name
        self.include_orphaned = include_orphaned
        self.order_by = order_by if order_by is not None else list()
        self.page_size = DEFAULT_PAGE_SIZE if page_size == 0 else page_size


class ActivitySearchService(ABC):

    @abstractmethod
    def search(self, search_query: SearchQuery) -> List[Activity]:
        """
        @param {SearchQuery} search query
        @returns {List[Activity]} results
        """
        # TODO implement pagination (P1)
        raise NotImplementedError("not implemented")
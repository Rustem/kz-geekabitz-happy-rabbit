from typing import List, Type

from django.db.models import Q

from happyrabbit.abc.activity import Activity
from happyrabbit.abc.service.activity import ActivitySearchService, SearchQuery, NextPageRequest, PaginatedResponse
from happyrabbit.activity.models import ActivityModel


class SearchQueryBuilder:

    def __init__(self):
        self.owner_id = None
        self.category_name = None
        self.include_orphaned = None

    def with_owner_id(self, owner_id: int):
        self.owner_id = owner_id
        return self

    def with_category_name(self, category_name: str):
        self.category_name = category_name
        return self

    def with_include_orphaned(self, include_orphaned: bool):
        self.include_orphaned = include_orphaned
        return self

    def build(self) -> SearchQuery:
        return SearchQuery(self.owner_id, self.category_name, include_orphaned=self.include_orphaned)


class DefaultActivitySearchService(ActivitySearchService):

    ALWAYS_TRUE = Q()
    ALWAYS_FALSE = Q(pk__in=[])

    def search(self, search_query: SearchQuery) -> List[Activity]:
        qs = ActivityModel.objects
        # TODO include indexes
        by_owner_id = Q(owner_id=search_query.owner_id) if search_query.owner_id else self.ALWAYS_TRUE
        by_category_name = Q(category__title=search_query.category_name) if search_query.category_name else self.ALWAYS_TRUE
        include_orphaned = Q(category__isnull=True) if search_query.include_orphaned else self.ALWAYS_FALSE
        qs = qs.filter(by_owner_id & (by_category_name | include_orphaned))
        if search_query.order_by:
            qs = qs.order_by(*search_query.order_by)
        matched = qs.all()
        if search_query.page_size:
            matched = matched[:search_query.page_size]
        return matched

    def search_paginated(self, search_query: SearchQuery) -> PaginatedResponse:
        pass

    def load_next_page(self, page_request: NextPageRequest) -> PaginatedResponse:
        pass


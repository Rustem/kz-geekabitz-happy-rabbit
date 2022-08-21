import binascii
import os
from typing import List, Type

from django.db.models import Q

from happyrabbit.abc.activity import Activity
from happyrabbit.abc.errors import PaginationNotFoundError, IllegalStateError
from happyrabbit.abc.service.activity import ActivitySearchService, SearchQuery, NextPageRequest, PaginatedResponse
from happyrabbit.activity.models import ActivityModel, ActivityPaginationModel, DEFAULT_ACTIVITY_PAGE_SIZE


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
        # if search_query.page_size:
        #     matched = matched[:search_query.page_size]
        return matched

    def search_paginated(self, search_query: SearchQuery) -> PaginatedResponse:
        # 1 make a search
        activities = self.search(search_query)
        total = len(activities)
        page_size = DEFAULT_ACTIVITY_PAGE_SIZE
        # 2 create instance of ActivityPagination
        # TODO if already exists then reuse one
        pagination = ActivityPaginationModel()
        pagination_token = pagination.pagination_token = ActivityPaginationModel.generate_key()
        pagination.min_index = 1
        pagination.max_index = int(total / page_size) + int((total % page_size > 0))
        pagination.query = search_query
        pagination.owner_id = search_query.owner_id
        # 3 save pagination
        pagination.save()
        pagination.refresh_from_db()
        # 4 prepare pagination response
        page_of_activities = activities[:page_size]
        next_page = NextPageRequest(2, pagination_token)
        return PaginatedResponse(page_of_activities, total, pagination_token, 1, pagination.max_index, next_page, None)

    def load_next_page(self, page_request: NextPageRequest) -> PaginatedResponse:
        # fetch from database
        pagination = ActivityPaginationModel.objects.filter(pagination_token=page_request.pagination_token).first()
        if not pagination:
            # if nothing found handle error
            raise PaginationNotFoundError(f'pagination for token [{page_request.pagination_token}] not found')
        cur_page = min(pagination.max_index, max(pagination.min_index, page_request.page))
        # TODO improve with limit offset
        start_inclusive = cur_page * (DEFAULT_ACTIVITY_PAGE_SIZE - 1) + 1
        end_exclusive = cur_page * DEFAULT_ACTIVITY_PAGE_SIZE + 1
        search_query = pagination.get_query()
        activities = self.search(search_query)
        if not activities:
            # TODO log suddenly no data, however a valid case since activities could be deleted
            return PaginatedResponse([], 0, page_request.pagination_token, cur_page, cur_page,
                                     None, cur_page > 1 and NextPageRequest(page_request.pagination_token, cur_page - 1) or None)
        count = len(activities)
        page_of_activities = activities[start_inclusive:end_exclusive]
        next, prev = None, None
        if cur_page < pagination.max_index:
            next = NextPageRequest(page_request.pagination_token, cur_page + 1)
        if cur_page > 1:
            prev = NextPageRequest(page_request.pagination_token, cur_page - 1)
        return PaginatedResponse(page_of_activities, count, page_request.pagination_token, cur_page, pagination.max_index, next, prev)

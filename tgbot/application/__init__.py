from typing import List

from django.contrib.auth.models import User
from telegram import Update

from happyrabbit.abc.activity import Activity
from happyrabbit.abc.errors import IllegalStateError
from happyrabbit.abc.external_account import ExternalSession
from happyrabbit.abc.service.activity import ActivitySearchService, SearchQuery, PaginatedResponse, NextPageRequest
from happyrabbit.abc.service.auth import BaseAuthService
from happyrabbit.abc.service.external_account import ExternalUserService
from happyrabbit.abc.service.family import BaseFamilyService
from happyrabbit.abc.service.tracking import ActivityTrackingService
from tgbot.service.activity import SearchQueryBuilder


class HappyRabbitApplication:
    auth_service: BaseAuthService
    external_user_service: ExternalUserService
    family_service: BaseFamilyService
    activity_search_service: ActivitySearchService
    activity_tracking_service: ActivityTrackingService

    def __init__(self,
                 auth_service: BaseAuthService,
                 external_user_service: ExternalUserService,
                 family_service: BaseFamilyService,
                 activity_search_service: ActivitySearchService,
                 activity_tracking_service: ActivityTrackingService):
        self.auth_service = auth_service
        self.external_user_service = external_user_service
        self.family_service = family_service
        self.activity_search_service = activity_search_service
        self.activity_tracking_service = activity_tracking_service

    def get_active_session(self, update: Update) -> ExternalSession:
        requester_account = self.external_user_service.extract_external_account(update)
        lookup_account = self.auth_service.get_account(requester_account.get_external_user_id())

        if not lookup_account:
            created_account = self.auth_service.create_account(requester_account, requester_account.get_external_profile())
            return self.auth_service.unauthenticated_session(created_account)

        session = self.auth_service.get_external_session(requester_account.get_external_user_id())
        if not session:
            return self.auth_service.unauthenticated_session(lookup_account)

        return session

    def search_activities(self, session: ExternalSession, category_name: str) -> PaginatedResponse:
        if not session.is_authenticated():
            raise IllegalStateError("user should be authenticated")
        owner_id = session.get_account().get_linked_user().pk
        search_query = SearchQueryBuilder()\
            .with_category_name(category_name)\
            .with_owner_id(owner_id)\
            .with_include_orphaned(False)\
            .build()
        results = self.activity_search_service.search_paginated(search_query)
        return results

    def load_next_page_of_activities(self, session: ExternalSession, page_request: NextPageRequest) -> PaginatedResponse:
        if not session.is_authenticated():
            raise IllegalStateError("user should be authenticated")
        results = self.activity_search_service.load_next_page(page_request)
        return results

    def get_children_display_names(self, user: User) -> List[str]:
        if user is None:
            return list()
        children = self.family_service.get_children(user.pk)
        return list(map(lambda kid: kid.get_name().capitalize(), children))

    def get_active_session_by_auth_key(self, session_key : str) -> ExternalSession | None:
        return self.auth_service.get_external_session_by_auth_key(session_key)

    def get_signin_url(self, external_user_id: int):
        return self.auth_service.get_deeplink_url(external_user_id)




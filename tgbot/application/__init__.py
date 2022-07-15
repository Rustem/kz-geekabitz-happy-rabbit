from telegram import Update

from happyrabbit.abc.external_account import ExternalSession
from happyrabbit.abc.service.auth import BaseAuthService
from happyrabbit.abc.service.external_account import ExternalUserService


class HappyRabbitApplication:
    auth_service: BaseAuthService
    external_user_service: ExternalUserService

    def __init__(self, auth_service: BaseAuthService, external_user_service: ExternalUserService):
        self.auth_service = auth_service
        self.external_user_service = external_user_service

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

    def get_active_session_by_auth_key(self, session_key : str) -> ExternalSession | None:
        return self.auth_service.get_external_session_by_auth_key(session_key)

    def get_signin_url(self, external_user_id: int):
        return self.auth_service.get_deeplink_url(external_user_id)




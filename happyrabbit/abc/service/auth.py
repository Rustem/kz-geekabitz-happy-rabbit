from abc import ABC, abstractmethod

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from happyrabbit.abc.external_account import AuthToken, ExternalAccount, ExternalSession, ExternalUserProfile


class AccountDoesNotExist(ValidationError):
    pass


class BaseAuthService(ABC):

    @abstractmethod
    def get_auth_token(self, user: User, account_id: int) -> AuthToken:
        f"""
        @param {int} account_id - external account identifier
        @returns {AuthToken} active auth token
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def get_account(self, external_user_id: int) -> ExternalAccount | None:
        f"""
        @param {int} external_user_id - external account identifier
        @returns {AuthToken} active auth token or {None}
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def link_user_to_account(self, user, account_id: int) -> ExternalAccount:
        """"""
        raise NotImplementedError("not implemented")

    def has_account(self, account_id: int):
        try:
            return self.get_account(account_id) and True or False
        except AccountDoesNotExist:
            return False

    def create_account(self, account: ExternalAccount, profile: ExternalUserProfile) -> ExternalAccount:
        f"""
        @param {ExternalAccount} external account (required)
        @param {ExternalUserProfile} profile (optional)
        @returns created account
        """
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_external_session(self, external_user_id: int) -> ExternalSession | None:
        f"""
        @returns {ExternalSession} account's session if exists, otherwise returns {None}
        """
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_external_session_by_auth_key(self, session_key: str) -> ExternalSession | None:
        raise NotImplementedError("not implemented")

    @abstractmethod
    def get_deeplink_url(self, external_user_id: int) -> str:
        """
        @returns {str} signin url to authenticate via deep link
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def unauthenticated_session(self, account: ExternalAccount) -> ExternalSession:
        f"""
        @returns {ExternalSession} instance of an unauthenticated session
        """
        pass



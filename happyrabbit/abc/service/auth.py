from abc import ABC, abstractmethod

from django.core.exceptions import ValidationError

from happyrabbit.abc.external_account import AuthToken, ExternalAccount


class AccountDoesNotExist(ValidationError):
    pass


class BaseAuthService(ABC):

    @abstractmethod
    def get_auth_token(self, account_id: int) -> AuthToken:
        f"""
        @param {int} account_id - external account identifier
        @returns {AuthToken} active auth token
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def get_account(self, account_id: int) -> ExternalAccount:
        f"""
        @param {int} account_id - external account identifier
        @throws AccountDoesNotExist - if account does not exist
        @returns {AuthToken} active auth token
        """
        raise NotImplementedError("Not implemented")

    def has_account(self, account_id: int):
        try:
            return self.get_account(account_id) and True or False
        except AccountDoesNotExist:
            return False

    @abstractmethod
    def get_deeplink_url(self, account_id: int) -> str:
        raise NotImplementedError("Not implemented")


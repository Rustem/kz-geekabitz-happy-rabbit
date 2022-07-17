from abc import ABC, abstractmethod

from happyrabbit.abc.external_account import ExternalAccount


class ExternalUserService(ABC):

    @abstractmethod
    def extract_external_account(self, external_data) -> ExternalAccount:
        """
        @param {any} external_data - update/response from external identity provider (service)
        @return parsed account
        """
        raise NotImplementedError("Not implemented")

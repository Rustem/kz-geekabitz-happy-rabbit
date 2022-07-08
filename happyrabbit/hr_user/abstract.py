import datetime
from abc import abstractmethod, ABCMeta


class ExternalUserProfile:

    @abstractmethod
    def get_first_name(self) -> str:
        pass

    @abstractmethod
    def get_last_name(self) -> str:
        pass

    @abstractmethod
    def get_language_code(self) -> str:
        pass

    @abstractmethod
    def get_username(self) -> str:
        pass


class ExternalAccount:

    @abstractmethod
    def get_external_service(self) -> str:
        pass

    @abstractmethod
    def get_external_user_id(self) -> int:
        pass

    @abstractmethod
    def get_external_profile(self) -> ExternalUserProfile:
        pass

    @abstractmethod
    def get_username(self) -> str:
        pass


class ExternalSession:

    @abstractmethod
    def get_session_id(self) -> str:
        pass

    @abstractmethod
    def get_account(self) -> ExternalAccount:
        pass

    @abstractmethod
    def get_date_logged_in(self) -> datetime.datetime:
        pass

    @abstractmethod
    def get_username(self) -> str:
        pass
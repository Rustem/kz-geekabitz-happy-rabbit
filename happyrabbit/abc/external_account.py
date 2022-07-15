import datetime
from abc import abstractmethod


TELEGRAM = 'TELEGRAM'
EXTERNAL_SERVICE_CHOICES = [
    (TELEGRAM, 'Telegram')
]

LANGUAGE_CODE_CHOICES = [
    ('RU', 'Русский'),
    ('EN', 'English'),
    ('KZ', 'Казахский')
]


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

    @abstractmethod
    def get_linked_user(self):
        pass

    @abstractmethod
    def is_linked_to_user(self, target_user) -> bool:
        """
        Checks if this account is linked to a `target_user`
        @returns {bool}
        """
        pass

    @abstractmethod
    def is_saved(self) -> bool:
        pass


class AuthToken:

    @abstractmethod
    def get_key(self) -> str:
        pass

    @abstractmethod
    def get_created(self) -> datetime.datetime:
        pass

    @abstractmethod
    def is_expired(self) -> bool:
        pass


class ExternalSession:

    @abstractmethod
    def get_session_id(self) -> str:
        pass

    @abstractmethod
    def get_auth_token(self) -> AuthToken:
        pass

    @abstractmethod
    def get_account(self) -> ExternalAccount:
        pass

    @abstractmethod
    def get_login_date(self) -> datetime.datetime:
        pass

    @abstractmethod
    def get_username(self) -> str:
        pass

    @abstractmethod
    def is_expired(self) -> bool:
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        pass
from django.core.exceptions import ValidationError

from happyrabbit.hr_user.abstract import AuthToken
from happyrabbit.hr_user.models import Session, AuthTokenModel, Account
from django.contrib.auth.models import User


class AuthError(ValidationError):
    pass


class AuthService:

    def get_auth_token(self, user: User, account_id: int) -> AuthToken:
        if not account_id:
            raise ValueError("account_id is required")
        account = self.get_account(account_id)

        session, created = Session.objects.get_or_create(account=account)
        if not created and session.is_expired():
            if session.auth_token is not None:
                session.auth_token.delete()
        return AuthTokenModel.objects.create(session=session)

    def get_account(self, account_id: int) -> Account:
        try:
            return Account.objects.get(pk=account_id)
        except Account.DoesNotExist as e:
            raise AuthError("account not found", e)

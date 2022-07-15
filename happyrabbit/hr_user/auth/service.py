from django.urls import reverse

from happyrabbit.abc.external_account import AuthToken, ExternalAccount
from happyrabbit.abc.service.auth import BaseAuthService, AccountDoesNotExist
from happyrabbit.hr_user.models import Session, AuthTokenModel, Account

ACCOUNT_DOES_NOT_EXIST = "Account [%s] does not exist"


class AuthService(BaseAuthService):

    def get_auth_token(self, account_id: int) -> AuthToken:
        print(account_id + "Acocunt")
        if not account_id:
            raise ValueError(ACCOUNT_DOES_NOT_EXIST % account_id)
        account = self.get_account(account_id)

        session, created = Session.objects.get_or_create(account=account)
        if not created and session.is_expired():
            if session.auth_token is not None:
                session.auth_token.delete()
        return AuthTokenModel.objects.create(session=session)

    def get_account(self, account_id: int) -> ExternalAccount:
        try:
            return Account.objects.get(pk=account_id)
        except Account.DoesNotExist as e:
            raise AccountDoesNotExist("account not found", e)

    def get_deeplink_url(self, account_id: int) -> str:
        if not self.has_account(account_id):
            raise AccountDoesNotExist(ACCOUNT_DOES_NOT_EXIST % account_id)
        return reverse('auth-deeplink', kwargs={"account_id": account_id})

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.sites.models import Site

from happyrabbit.abc.errors import IllegalStateError, IllegalArgumentError
from happyrabbit.abc.external_account import AuthToken, ExternalAccount, ExternalSession, TELEGRAM, ExternalUserProfile
from happyrabbit.abc.service.auth import BaseAuthService, AccountDoesNotExist
from happyrabbit.hr_user.models import Session, AuthTokenModel, Account, UserProfile

ACCOUNT_DOES_NOT_EXIST = "Account [%s] does not exist"


class AuthService(BaseAuthService):

    def create_account(self, account: ExternalAccount, profile: ExternalUserProfile):
        if not account:
            raise IllegalArgumentError("account is null")
        if account.is_saved():
            raise IllegalStateError("Account is already created")
        created_account = Account.objects.create(
            external_service=TELEGRAM,
            external_user_id=account.get_external_user_id())
        if profile:
            created_account.userprofile = UserProfile.objects.create(
                first_name=profile.get_first_name(),
                last_name=profile.get_last_name(),
                language_code=profile.get_language_code(),
                username=profile.get_username(),
                # relationships
                account=created_account
            )
        return created_account

    def link_user_to_account(self, user, external_user_id: int) -> ExternalAccount:
        account = self.get_account(external_user_id)
        account.user = user
        account.save()
        return account

    def get_account(self, external_user_id: int) -> ExternalAccount | None:
        try:
            return Account.objects.get(external_user_id=external_user_id)
        except Account.DoesNotExist as e:
            return None

    def unauthenticated_session(self, external_account: ExternalAccount) -> ExternalSession:
        if not external_account.is_saved():
            raise IllegalStateError("External account has to be created")
        return Session(account=external_account)

    def get_external_session(self, external_user_id: int) -> ExternalSession | None:
        try:
            return Session.objects.get(account__external_user_id=external_user_id)
        except Session.DoesNotExist:
            return None

    def get_external_session_by_auth_key(self, session_key: str) -> ExternalSession | None:
        return Session.objects.filter(auth_token__key=session_key).first()

    def get_auth_token(self, user: User, account_id: int) -> AuthToken:
        if not account_id:
            raise IllegalArgumentError(ACCOUNT_DOES_NOT_EXIST % account_id)
        account = self.get_account(account_id)

        if not account.is_linked_to_user(user):
            raise ValidationError("Requested user is not linked to this account")

        if not user.is_authenticated:
            raise ValidationError("user is not authenticated")

        session, created = Session.objects.get_or_create(account=account)
        if not created and session.is_expired():
            if session.auth_token is not None:
                session.auth_token.delete()
        auth_token = AuthTokenModel.objects.create()
        session.auth_token = auth_token
        session.save()
        return auth_token

    def get_deeplink_url(self, external_user_id: int) -> str:
        domain = Site.objects.get_current().domain
        if not self.has_account(external_user_id):
            raise AccountDoesNotExist(ACCOUNT_DOES_NOT_EXIST % external_user_id)
        relative_url = reverse('auth-deeplink', kwargs={"account_id": external_user_id})
        # TODO replace http with scheme
        return f'http://{domain}{relative_url}'

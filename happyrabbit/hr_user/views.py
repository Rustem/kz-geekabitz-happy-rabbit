from django.views.generic import TemplateView
from django.conf import settings

from happyrabbit.hr_user.auth.service import AuthService

TELEGRAM_USERNAME = settings.TELEGRAM_USERNAME


class AuthDeepLinkView(TemplateView):
    template_name = 'hr_user/deep_link.html'

    auth_service: AuthService

    def __init__(self, **kwargs):
        super().__init__()
        self.auth_service = AuthService()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['bot_deeplink'] = self._generate_deeplink(kwargs['account_id'])
        return kwargs

    def _generate_deeplink(self, account_id: int) -> str:
        auth_token = self.auth_service.get_auth_token(self.request.user, account_id)
        return f'http://t.me/{TELEGRAM_USERNAME}?start={auth_token.get_key()}'


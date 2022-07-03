from abc import ABC, abstractmethod
from typing import Dict

from telegram import Update

from happyrabbit.hr_user.abstract import ExternalAccount
from happyrabbit.hr_user.enums import TELEGRAM
from happyrabbit.hr_user.models import Account, UserProfile


class ExternalUserBackend(ABC):

    @abstractmethod
    def extract_external_profile(self, external_data) -> ExternalAccount:
        pass


class TelegramUserBackend(ExternalUserBackend):

    def extract_external_profile(self, external_data: Update) -> ExternalAccount:
        """ python-telegram-bot's Update instance --> User info """
        user = self._extract_user_data(external_data)
        if user is None:
            raise Exception(f"Can't extract user data from update: {external_data}")
        # TODO if user is bot then throw error
        external_account = Account(external_service=TELEGRAM, external_user_id=user['id'])
        external_account.userprofile = UserProfile(
            username=user['username'],
            first_name=user['first_name'],
            last_name=user.get('last_name', None),
            language_code=user.get('language_code', None))
        return external_account

    @staticmethod
    def _extract_user_data(external_data: Update) -> Dict:
        if external_data.message is not None:
            return external_data.message.from_user.to_dict()
        elif external_data.inline_query is not None:
            return external_data.inline_query.from_user.to_dict()
        elif external_data.chosen_inline_result is not None:
            return external_data.chosen_inline_result.from_user.to_dict()
        elif external_data.callback_query is not None and external_data.callback_query.from_user is not None:
            return external_data.callback_query.from_user.to_dict()
        elif external_data.callback_query is not None and external_data.callback_query.message is not None:
            return external_data.callback_query.message.chat.to_dict()
        return None

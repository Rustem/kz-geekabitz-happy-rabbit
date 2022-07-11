from tgbot.backends import TelegramUserBackend
from tgbot.core.dialogs.base import MessageDialog


class AuthenticationDialog(MessageDialog):
    telegram_user_backend: TelegramUserBackend

    def __init__(self, telegram_user_backend: TelegramUserBackend):
        self.telegram_user_backend = telegram_user_backend

    def step1(self):
        raise NotImplementedError("not implemented")

    step1_message = "Enter login"

    def step1_options(self):
        raise NotImplementedError("Implement me")

    def cancel(self) -> bool:
        raise NotImplementedError("Implement me")
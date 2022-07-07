from tgbot.core.dialogs.base import MessageDialog


class AuthDialog(MessageDialog):

    def step1(self):
        raise NotImplementedError("not implemented")

    step1_message = "Enter login"

    def step1_options(self):
        raise NotImplementedError("Implement me")

    def cancel(self) -> bool:
        raise NotImplementedError("Implement me")
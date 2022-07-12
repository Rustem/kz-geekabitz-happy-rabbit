import logging

from happyrabbit.abc.external_account import ExternalAccount
from happyrabbit.hr_user.models import Session, Account, UserProfile
from tgbot.core import messages
from tgbot.core.base_bot import BaseBot
from tgbot.core.context import ConversationContext

logger = logging.getLogger(__name__)


def user_display(account: ExternalAccount):
    return "{}:{}".format(account.get_external_user_id(), account.get_username())


def log_command(context: ConversationContext, cmd_name: str):
    message = "/{cmd_name} command was issued by {user} in {chat}"
    logger.info(message.format(
        cmd_name=cmd_name,
        user=user_display(context.session.get_account()),
        chat=context.session.get_session_id()))


class HappyRabbitBot(BaseBot):

    def __init__(self, telegram_token: str):
        super().__init__(telegram_token)
        logger.debug("Create new instance of TrelloBot.")

        bot_info = self.bot.get_me()
        bot_link = f"https://t.me/" + bot_info["username"]
        logging.info(f"Pooling of '{bot_link}' started")

    def cmd_start(self, context: ConversationContext):
        # TODO extract auth key
        if not context.text:
            pass
        # if session is part of context and session is active then return appropriate message
        # otherwise using auth key query session
            # if session is found then authenticate user
            # if session is not found then ask user to login with login url
        pass

    def cmd_help(self, context: ConversationContext):
        # TODO return List of available commands with descriptions
        raise NotImplementedError("Implement me")

    def cmd_status(self, context: ConversationContext):
        # TODO return detailed authentication status
        raise NotImplementedError("Implement me")

    def wrap_context(self, context: ConversationContext):
        # TODO move to backend
        # 1 search session by external_user_id
        # 2 if session is found than include user session as part of converation context
        # 3 if session is not found, then don't include session
        user = context.message.from_user
        account = Account(external_user_id=user.id)
        account.userprofile = UserProfile(username=user.username)
        session = Session(session_id=context.chat_id, account=account)
        # session, created = Session.objects.get_or_create(session_id=context.chat_id)
        context.set_session(session)
        return context

    def command_not_found(self, context):
        self.message_sender.send_message_for_context(context, messages.COMMAND_NOT_FOUND.format(command=context.text))


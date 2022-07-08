import logging

from happyrabbit.hr_user.abstract import ExternalAccount
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

    def cmd_auth(self, context: ConversationContext):
        log_command(context, "auth")

        if context.session.get_username():
            logger.debug("...Already authorized as %s.", context.session.get_username())
            self.message_sender.send_message_for_context(context, messages.AUTH_ALREADY)
            return

        # TODO: Add groups authorization
        # TODO authenticate

    def cmd_unauth(self, context: ConversationContext):
        raise NotImplementedError("Implement me")

    def cmd_help(self, context: ConversationContext):
        raise NotImplementedError("Implement me")

    def cmd_status(self, context: ConversationContext):
        raise NotImplementedError("Implement me")

    def wrap_context(self, context: ConversationContext):
        # TODO move to backend
        user = context.message.from_user
        account = Account(external_user_id=user.id)
        account.userprofile = UserProfile(username=user.username)
        session = Session(session_id=context.chat_id, account=account)
        # session, created = Session.objects.get_or_create(session_id=context.chat_id)
        context.set_session(session)
        return context


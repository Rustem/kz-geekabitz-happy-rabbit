import logging

from happyrabbit.abc.external_account import ExternalAccount
from happyrabbit.hr_user.models import Session, Account, UserProfile
from tgbot.application import HappyRabbitApplication
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

    happy_rabbit_app: HappyRabbitApplication

    def __init__(self, happy_rabbit_app: HappyRabbitApplication, telegram_token: str):
        super().__init__(telegram_token)
        self.happy_rabbit_app = happy_rabbit_app
        logger.debug("Create new instance of TrelloBot.")

        bot_info = self.bot.get_me()
        bot_link = f"https://t.me/" + bot_info["username"]
        logging.info(f"Pooling of '{bot_link}' started")

    def cmd_start(self, context: ConversationContext):
        if not context.args:
            # /start <-> command without args
            # 1. check if account has an active session
            session = self.happy_rabbit_app.get_active_session(context.update)
            if session.is_authenticated():
                # 2. if session is already authenticated => welcome user
                user = session.get_account().get_linked_user()
                # TODO simplify and extract some markdown functions into utility class
                children_names = ', '.join(map(lambda name: f'*{name}*',
                                               self.happy_rabbit_app.get_children_display_names(user)))
                self.message_sender.send_message_for_context(context, messages.WELCOME_AUTHENTICATED_USER.format(
                    username=session.get_username(), children=children_names))
                return
            if session.is_expired():
                # 3. if session is not authenticated
                assert session.get_account() is not None
                # todo include message
                login_url = self.happy_rabbit_app.get_signin_url(session.get_account().get_external_user_id())
                self.message_sender.send_message_for_context(context, messages.LOGIN_REQUIRED.format(login_url=login_url))
                return
        else:
            # /start {session_key}
            auth_key = context.args[0]
            session = self.happy_rabbit_app.get_active_session_by_auth_key(auth_key)
            if session is None:
                # @note: get user_id from a conversation context update
                login_url = self.happy_rabbit_app.get_signin_url(context.external_user_id)
                self.message_sender.send_message_for_context(context,
                                                             messages.INVALID_AUTH_KEY.format(login_url=login_url))
                return
            if session.is_expired():
                login_url = self.happy_rabbit_app.get_signin_url(session.get_account().get_external_user_id())
                self.message_sender.send_message_for_context(context, messages.WELCOME_NOT_AUTHENTICATED_USER.format(
                    username=session.get_username(), login_url=login_url))
                return
            # session is authenticated
            user = session.get_account().get_linked_user()
            children_names = ', '.join(self.happy_rabbit_app.get_children_display_names(user))
            self.message_sender.send_message_for_context(context,
                                                         messages.WELCOME_AUTHENTICATED_USER.format(username=session.get_username(),
                                                                                                    children=children_names))


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


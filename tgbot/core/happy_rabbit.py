import logging
from tgbot.application import HappyRabbitApplication
from tgbot.core import messages
from tgbot.core.base_bot import BaseBot
from tgbot.core.callback_handlers import TgInlineCallbackHandler, PaginationCallbackHandler, PaginationEvent
from tgbot.core.context import ConversationContext
from tgbot.core.decorators import command_handler, command_registry, auth_required
from tgbot.core.formatters.activity import inline_activity_list
from tgbot.core.markup.pagination import PaginationKeyboardMarkup

logger = logging.getLogger(__name__)


def log_command(context: ConversationContext, cmd_name: str):
    message = "/{cmd_name} command was issued by {user} in {chat}"
    logger.info(message.format(
        cmd_name=cmd_name,
        user=context.user_display(),
        chat=context.session.get_session_id()))


class HappyRabbitBot(BaseBot):

    happy_rabbit_app: HappyRabbitApplication

    callback_handler: TgInlineCallbackHandler

    def __init__(self, happy_rabbit_app: HappyRabbitApplication, telegram_token: str):
        super().__init__(telegram_token)
        self.happy_rabbit_app = happy_rabbit_app
        logger.debug("Create new instance of TrelloBot.")

        bot_info = self.bot.get_me()
        bot_link = f"https://t.me/" + bot_info["username"]
        logging.info(f"Pooling of '{bot_link}' started")
        self.initialize()

    def initialize(self):
        self.initialize_callback_handler(self.happy_rabbit_app)

    def initialize_callback_handler(self, happy_rabbit_app):
        callback_handlers = (
            PaginationCallbackHandler(happy_rabbit_app),
        )
        self.callback_handler = TgInlineCallbackHandler(callback_handlers)


    @command_handler(description="To start your Happy Rabbit experience")
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

    @command_handler(description="To learn more about supported commands")
    def cmd_help(self, context: ConversationContext):
        # TODO return List of available commands with descriptions
        available_commands = '\n'.join('{} - {}'.format(key, value)
                                       for key, value in command_registry.items())
        self.message_sender.send_message_for_context(context, messages.HELP.format(available_commands=available_commands))

    @auth_required
    @command_handler(description="To learn more details about an active session")
    def cmd_status(self, context: ConversationContext):
        session = self.happy_rabbit_app.get_active_session(context.update)
        if session.is_authenticated():
            login_date = session.get_login_date().strftime("%Y-%m-%d %H:%M:%S")
            self.message_sender.send_message_for_context(context,
                                                         messages.STATUS_OK.format(username=session.get_username(), date_logged_in=login_date))
            return
        if session.is_expired():
            self.message_sender.send_message_for_context(context, messages.STATUS_INVALID_TOKEN)
            return

    @auth_required
    @command_handler(description="To get a list of activities for a specified category")
    def cmd_show_activities(self, context: ConversationContext):
        if not context.args:
            self.message_sender.send_message_for_context(context, messages.SHOW_ACTIVITIES_MISS_CATEGORY)
            return
        else:
            category_name = context.args[0]
            activities_page = self.happy_rabbit_app.search_activities(context.session, category_name)
            # TODO if no activities ?
            reply_markup = PaginationKeyboardMarkup(activities_page.total_pages,
                                                    activities_page.pagination_token,
                                                    activities_page.page_number,
                                                    callback_data_provider=PaginationEvent.create)
            # reply_markup
            inline_activities = inline_activity_list(activities_page.page_number, activities_page.items)
            self.message_sender.send_message_for_context(context,
                                                         messages.SHOW_ACTIVITIES_OK.format(inline_activities=inline_activities),
                                                         reply_markup=reply_markup.to_markup())
            return

    @auth_required
    @command_handler(description="Renumerate a child with carrots for doing activity")
    def cmd_activities_for(self, context: ConversationContext):
        raise NotImplementedError("implement soon")

    @auth_required
    def callback_query_handler(self, context: ConversationContext):
        self.callback_handler.handle(context)

    def wrap_context(self, context: ConversationContext):
        session = self.happy_rabbit_app.get_active_session(context.update)
        context.set_session(session)
        return context

    def command_not_found(self, context):
        self.message_sender.send_message_for_context(context, messages.COMMAND_NOT_FOUND.format(command=context.text))


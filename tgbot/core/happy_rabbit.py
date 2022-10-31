import logging
from typing import List

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters, Filters

from happyrabbit.activity.models import CONFIGURED_ACTIVITY_PAGE_SIZE
from tgbot.application import HappyRabbitApplication
from tgbot.core import messages
from tgbot.core.base_bot import BaseBot
from tgbot.core.callback_handlers import TgInlineCallbackHandler, PaginationCallbackHandler, PaginationEvent
from tgbot.core.context import ConversationContext
from tgbot.core.decorators import command_handler, command_registry, auth_required
from tgbot.core.dialogs.record_activity import RecordActivityDialog
from tgbot.core.markup.pagination import PaginationKeyboardMarkup
from tgbot.core.renderer.django_template import DjangoTemplateRenderer

logger = logging.getLogger(__name__)


def log_command(context: ConversationContext, cmd_name: str):
    message = "/{cmd_name} command was issued by {user} in {chat}"
    logger.info(message.format(
        cmd_name=cmd_name,
        user=context.user_display(),
        chat=context.session.get_session_id()))


CHILD_CHOICE, ACTIVITY_CHOICE, REWARD_CHOICE, DONE = range(4)


class HappyRabbitBot(BaseBot):

    happy_rabbit_app: HappyRabbitApplication

    callback_handler: TgInlineCallbackHandler

    template_renderer: DjangoTemplateRenderer

    def __init__(self, happy_rabbit_app: HappyRabbitApplication, telegram_token: str):
        super().__init__(telegram_token)
        self.happy_rabbit_app = happy_rabbit_app
        logger.debug("Create new instance of TrelloBot.")

        bot_info = self.bot.get_me()
        bot_link = f"https://t.me/" + bot_info["username"]
        logging.info(f"Pooling of '{bot_link}' started")
        self.initialize()

    def initialize(self):
        self.initialize_template_renderer()
        self.initialize_callback_handler()

    def initialize_callback_handler(self):
        callback_handlers = (
            PaginationCallbackHandler(self.happy_rabbit_app, self.template_renderer),
        )
        self.callback_handler = TgInlineCallbackHandler(callback_handlers)

    def initialize_template_renderer(self):
        self.template_renderer = DjangoTemplateRenderer()

    def add_conversation_handlers(self) -> List[ConversationHandler]:
        # Include more conversation handlers if needed
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("record_activity", self._wrap_cmd(self.cmd_record_activity))],
            states={
                CHILD_CHOICE: [
                    MessageHandler(
                        Filters.regex("^Start"), self._wrap_cmd(self.record_activity_child_choice)
                    ),
                ],
                # ACTIVITY_CHOICE: [
                #     CallbackQueryHandler(self._wrap_cmd(self.callback_query_handler), pass_user_data=True)
                # ],
                # REWARD_CHOICE: [
                #     CallbackQueryHandler(self._wrap_cmd(self.callback_query_handler), pass_user_data=True)
                # ],
                # RECORD_ACTIVITY_DONE: [
                #     # TODO
                # ]
            },
            fallbacks=[]
        )

        return []

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
                self.message_sender.send_message_for_context(context,
                                                             messages.LOGIN_REQUIRED.format(login_url=login_url))
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
                                                         messages.WELCOME_AUTHENTICATED_USER.format(
                                                             username=session.get_username(),
                                                             children=children_names))

    @command_handler(description="To learn more about supported commands")
    def cmd_help(self, context: ConversationContext):
        # TODO return List of available commands with descriptions
        available_commands = '\n'.join('{} - {}'.format(key, value)
                                       for key, value in command_registry.items())
        self.message_sender.send_message_for_context(context,
                                                     messages.HELP.format(available_commands=available_commands))

    @auth_required
    @command_handler(description="To learn more details about an active session")
    def cmd_status(self, context: ConversationContext):
        session = self.happy_rabbit_app.get_active_session(context.update)
        if session.is_authenticated():
            login_date = session.get_login_date().strftime("%Y-%m-%d %H:%M:%S")
            self.message_sender.send_message_for_context(context,
                                                         messages.STATUS_OK.format(username=session.get_username(),
                                                                                   date_logged_in=login_date))
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
            # TODO move number_offset under paginated response items
            rendered_text = self.template_renderer.render("activities/show_activities.txt",
                                                     number_offset=(activities_page.page_number - 1) * CONFIGURED_ACTIVITY_PAGE_SIZE,
                                                     activities=activities_page.items,
                                                     category_name=category_name,
                                                     page_number=activities_page.page_number)
            self.message_sender.send_message_for_context(context, rendered_text, reply_markup=reply_markup.to_markup())
            return

    @auth_required
    @command_handler(description="Renumerate a child with carrots for completing an activity")
    def cmd_record_activity(self, context: ConversationContext) -> int:
        # reply_keyboard = [
        #     ['Start'],
        #     ['Cancel'],
        # ]
        # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        text = self.template_renderer.render("record_activities/intro.txt",
                                             username=context.session.get_username())
        self.message_sender.send_message_for_context(context, text)
        dialog = RecordActivityDialog(self.message_sender)
        # TODO log dialog
        self.start_dialog(context, dialog)
        return CHILD_CHOICE

    @auth_required
    def record_activity_child_choice(self, context: ConversationContext) -> int:
        text = "Safina or Sander"
        self.message_sender.send_message_for_context(context, text)
        return ConversationHandler.END

    def record_activity_done(self, context: ConversationContext) -> int:
        print("record activity done")
        return ConversationHandler.END

    @auth_required
    def callback_query_handler(self, context: ConversationContext):
        result = self.callback_handler.handle(context)
        if result is not None and isinstance(result, int):
            logger.info("Next conversation handler state is %s", result)
            return result

    def wrap_context(self, context: ConversationContext):
        session = self.happy_rabbit_app.get_active_session(context.update)
        context.set_session(session)
        return context

    def command_not_found(self, context):
        self.message_sender.send_message_for_context(context, messages.COMMAND_NOT_FOUND.format(command=context.text))

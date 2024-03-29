import logging

from happyrabbit.abc.errors import IllegalArgumentError
from tgbot.core import messages
from tgbot.core.context import ConversationContext

logger = logging.getLogger(__name__)

command_registry = dict()
callback_handler_registry = dict()


def get_command_name(cmd_func):
    func_name = cmd_func.__name__
    if not func_name.startswith('cmd_'):
        raise IllegalArgumentError("Command handler should have the following name: cmd_{\\w+} i.e. cmd_help")
    return '/' + func_name[4:].replace('_', '\\_')


def command_handler(description=None):
    def wrapped_handler(cmd_func):
        def wrapper(base_bot, context: ConversationContext):
            cmd_func(base_bot, context)

        if description is None:
            raise IllegalArgumentError("Please provide description of a command")
        name = command_handler.name = get_command_name(cmd_func)
        command_handler.description = description
        command_registry[name] = description

        return wrapper
    return wrapped_handler


def auth_required(fn):
    def wrapper(self, ctx, *args, **kwargs):
        if not ctx.get_session().is_authenticated():
            logger.info(
                "{user} attempted to run command {name} in {chat} unauthorized".format(
                    user=ctx.user_display(),
                    chat=ctx.get_session().get_session_id(),
                    name=fn.__name__))
            self.message_sender.send_message_for_context(ctx, messages.STATUS_INVALID_TOKEN)
            return
        fn(self, ctx, *args, **kwargs)

    wrapper.__name__ = fn.__name__
    wrapper.__qualname__ = fn.__qualname__
    return wrapper
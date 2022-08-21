import logging
from typing import Callable

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


def get_callback_handler_name(cmd_func):
    func_name = cmd_func.__name__
    if not func_name.startswith('cb_'):
        raise IllegalArgumentError("Command handler should have the following name: cmd_{\\w+} i.e. cmd_help")
    return func_name[3:]


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


def inline_callback_handler(description=None):
    def wrapped_handler(callback_func):
        def wrapper(base_bot, context: ConversationContext):
            return callback_func(base_bot, context)

        name = inline_callback_handler.name = get_callback_handler_name(callback_func)
        callback_handler_registry[name] = callback_func

        return wrapper
    return wrapped_handler


def get_inline_callback_handler(handler_name) -> Callable:
    global callback_handler_registry
    callback_handler = callback_handler_registry.get(handler_name, None)
    if not callback_handler:
        raise IllegalArgumentError(f'callback handler [{handler_name}] not registered')
    return callback_handler


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
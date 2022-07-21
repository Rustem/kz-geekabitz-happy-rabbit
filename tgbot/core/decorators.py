from happyrabbit.abc.errors import IllegalArgumentError
from tgbot.core.context import ConversationContext

command_registry = dict()


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

from tgbot.core.context import ConversationContext


def command_handler(cmd_func):
    def wrapper(base_bot, context: ConversationContext):
        cmd_func()

    return wrapper

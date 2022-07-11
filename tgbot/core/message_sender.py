from typing import List

from telegram import Bot

from tgbot.core.context import ConversationContext


class MessageSender:
    """
    instance of telegram Bot
    """
    bot: Bot

    def __init__(self, bot: Bot):
        self.bot = bot

    def send_message_for_context(self, context: ConversationContext, text, **kwargs):
        self.send_message(context.chat_id, text, reply_to=context.reply_to, **kwargs)

    def send_message(self, chat_id: int, text: str, *,
                     options: List[List[str]] = None,
                     reply_to: int = None):
        if options:
            reply_markup = self.options_to_reply_markup(options)
        else:
            reply_markup = {'hide_keyboard': True}
        self.bot.send_message(chat_id=chat_id,
                              text=text,
                              parse_mode="Markdown",
                              reply_markup=reply_markup,
                              reply_to_message_id=reply_to)

    @staticmethod
    def options_to_reply_markup(options: List[List[str]]):
        keyboard = []

        for row in options:
            if isinstance(row, str):
                row = [row]
            keyboard.append([{'text': o} for o in row])

        return {
            'keyboard': keyboard,
            'one_time_keyboard': True,
            'selective': True,
        }

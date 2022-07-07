from typing import List

from telegram import Update, Bot
from telegram.message import Message


class ConversationContext:
    bot: Bot = None

    update: Update = None

    args: List[str] = None

    def __init__(self, bot: Bot, update: Update, args: List[str]=None):
        self.bot = bot
        self.update = update
        self.args = args or []

    @property
    def message(self) -> Message:
        return self.update.message

    @property
    def chat_id(self):
        return self.message.chat_id

    @property
    def text(self):
        return self.message.text

    @property
    def reply_to(self):
        if self.message.chat.type != 'private':
            return self.message.message_id
        else:
            return None


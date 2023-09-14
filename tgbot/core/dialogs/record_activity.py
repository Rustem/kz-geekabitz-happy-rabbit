from telegram import ReplyKeyboardMarkup

from tgbot.core.context import ConversationContext
from tgbot.core.dialogs.base import MessageDialog


class RecordActivityDialog(MessageDialog):
    """
    Record activity in four steps:
      step-1: pick a child
      step-2: pick activity
      step-3: pick reward
      step-4: collect
    """

    def step1(self, context: ConversationContext):
        print("step-1", context.text)
        # TODO implement handlign
        # store child pickup in buffer
        return True

    def step1_message(self, context: ConversationContext):
        return self.template_renderer.render("record_activities/select_child.txt")

    def step1_options(self, context: ConversationContext):
        # retrieve children
        select_children_keyboard = [
            ["Safina"],
            ["Sander"]
        ]
        return ReplyKeyboardMarkup(select_children_keyboard, one_time_keyboard=True)

    def cancel(self, context: ConversationContext) -> bool:
        self.message_sender.send_message_for_context(context, "Record of the activity was cancelled.")

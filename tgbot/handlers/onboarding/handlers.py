from telegram import Update

from typing import Dict

from telegram.ext import CallbackContext

from . import static_text
from .keyboards import make_keyboard_for_start_command


def extract_user_data_from_update(update: Update) -> Dict:
    """ python-telegram-bot's Update instance --> User info """
    if update.message is not None:
        user = update.message.from_user.to_dict()
    elif update.inline_query is not None:
        user = update.inline_query.from_user.to_dict()
    elif update.chosen_inline_result is not None:
        user = update.chosen_inline_result.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.from_user is not None:
        user = update.callback_query.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.message is not None:
        user = update.callback_query.message.chat.to_dict()
    else:
        raise Exception(f"Can't extract user data from update: {update}")

    return dict(
        user_id=user["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )

def command_start(update: Update, context: CallbackContext) -> None:
    tg_user = extract_user_data_from_update(update)
    # transform to Account object
    text = static_text.start_created.format(first_name=tg_user["first_name"])
    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())

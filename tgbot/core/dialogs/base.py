from abc import ABC, abstractmethod
from typing import List, Callable, Tuple, Type

from happyrabbit.abc.errors import IllegalStateError, IllegalArgumentError
from tgbot.core.context import ConversationContext
from tgbot.core.message_sender import MessageSender
from tgbot.core.renderer.django_template import DjangoTemplateRenderer


class DialogStateError(IllegalStateError):
    """
    Raises for cases that causes illegal dialog state
    """
    pass


class DialogState:
    steps: List[Tuple[int, Callable]] = None

    def __init__(self, steps: List[Tuple[int, Callable]]):
        self.steps = steps

    @property
    def current_step(self) -> Tuple[int, Callable]:
        return self.steps[0]

    def is_completed(self) -> bool:
        return len(self.steps) == 0

    def advance_next(self):
        self.steps = self.steps[1:]


class Dialog(ABC):
    dialog_state: DialogState = None

    def __init__(self):
        learnt_steps = self.learn_steps()
        self.dialog_state = DialogState(learnt_steps)

    def learn_steps(self) -> List[Tuple[int, Callable]]:
        steps = []
        for key in dir(self):
            if not key.startswith('step'): continue

            try:
                suffix = key[4:]
                if not suffix.isnumeric():
                    continue
                num = int(key[4:])
            except (ValueError, TypeError) as e:
                raise IllegalStateError("step function naming convention: step_[0-9](*args)", e)

            step_func = getattr(self, key)
            steps.append((num, step_func))
        return sorted(steps, key=lambda s: s[0])

    def execute_current_turn(self, context: ConversationContext):
        self.execute_turn(self.dialog_state.current_step, context)

    def advance_next(self, context: ConversationContext) -> bool:
        """
        Advances the dialog by executing step.
        @returns {bool} if dialog is completed, returns true, false otherwise.
        """
        if self.dialog_state.is_completed():
            raise DialogStateError("Dialog.advance_next called after dialog is completed.")

        if self.handle_turn(self.dialog_state.current_step, context):
            self.dialog_state.advance_next()

        if self.dialog_state.is_completed():
            return True

        self.execute_turn(self.dialog_state.current_step, context)
        return False

    @abstractmethod
    def execute_turn(self, step: Tuple[int, Callable], context: ConversationContext):
        f"""Service (bot) requests information from the user for this step
        @param {Tuple[int, Callable]} step to execute
        @param {ConversationContext} context a conversation context
        """
        raise NotImplementedError("derived class will implement")

    @staticmethod
    def handle_turn(step: Tuple[int, Callable[[ConversationContext], bool]], context: ConversationContext) -> bool:
        f"""Service (bot) processes collected information from the user. 
        """
        if step is None or len(step) != 2:
            raise IllegalArgumentError("expect step to be a non-nullable tuple[int, callable]")
        # TODO log execution
        step_num, step_func = step
        return step_func(context)

    @abstractmethod
    def cancel(self, context: ConversationContext) -> bool:
        raise NotImplementedError("derived class can implement me")


class MessageDialog(Dialog, ABC):
    message_sender: MessageSender
    template_renderer: DjangoTemplateRenderer

    def __init__(self, message_sender: MessageSender):
        super().__init__()
        self.message_sender = message_sender
        self.template_renderer = DjangoTemplateRenderer()

    def execute_turn(self, step: Tuple[int, Callable], context: ConversationContext):
        handler = step[1]
        resolve_msg = getattr(self, handler.__name__ + '_message', "...")
        msg = resolve_msg(context) if callable(resolve_msg) else resolve_msg

        resolve_options = getattr(self, handler.__name__ + '_options', None)
        options = resolve_options(context) if callable(resolve_options) else resolve_options
        print("Execute dialgo turn", msg, options, resolve_options(context))
        self.notify_recipient(context, msg, options)

    def notify_recipient(self, context: ConversationContext, text, options):
        self.message_sender.send_message_for_context(context, text, reply_markup=options)

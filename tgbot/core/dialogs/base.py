from abc import ABC, abstractmethod
from typing import List, Callable, Tuple, Type

from tgbot.core.context import ConversationContext
from tgbot.core.message_sender import MessageSender


class DialogStateError(ValueError):
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
                num = int(key[4:])
            except (ValueError, TypeError) as e:
                raise ValueError("step function naming convention: step_[0-9](*args)", e)

            step_func = getattr(self, key)
            steps.append((num, step_func))
        return sorted(steps, key=lambda s: s[0])

    def advance_next(self, context: ConversationContext) -> bool:
        """
        Advances the dialog by executing step.
        @returns {bool} if dialog is completed, returns true, false otherwise.
        """
        if self.dialog_state.is_completed():
            raise DialogStateError("Dialog.advance_next called after dialog is completed.")

        if self.execute_step(self.dialog_state.current_step, context):
            self.dialog_state.advance_next()

        if self.dialog_state.is_completed():
            return True

        self.on_step_completed(self.dialog_state.current_step, context)
        return False

    @abstractmethod
    def on_step_completed(self, step: Tuple[int, Callable], context: ConversationContext):
        f"""A hook to send a signal back to originator about a just completed dialog step with conversation context
        @param {Tuple[int, Callable]} step to execute
        @param {ConversationContext} context a conversation context
        """
        raise NotImplementedError("derived class will implement")

    @abstractmethod
    def cancel(self) -> bool:
        raise NotImplementedError("derived class can implement me")

    @staticmethod
    def execute_step(step: Tuple[int, Callable[[ConversationContext], bool]], context: ConversationContext) -> bool:
        if step is None or len(step) != 2:
            raise ValueError("expect step to be a non-nullable tuple[int, callable]")
        # TODO log execution
        step_num, step_func = step
        return step_func(context)


class MessageDialog(Dialog, ABC):
    message_sender: MessageSender

    def __init__(self, message_sender: MessageSender):
        super().__init__()
        self.message_sender = message_sender

    def on_step_completed(self, step: Tuple[int, Callable], context: ConversationContext):
        step_fn = step[1]
        options = getattr(self, step_fn.__name__ + '_options', None)
        text = getattr(self, step_fn.__name__ + '_message', "...")
        self.message_sender.send_message_for_context(context, text, options=options)

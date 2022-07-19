class IllegalStateError(RuntimeError):
    """
    @raises when a method is invoked at an illegal or inappropriate time
    """
    pass


class IllegalArgumentError(RuntimeError):
    """
    @raises to indicate that a method has been passed an illegal or inappropriate argument.
    """
    pass

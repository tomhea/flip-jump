class FlipJumpException(Exception):
    pass


class FlipJumpParsingException(FlipJumpException):
    pass


class FlipJumpPreprocessorException(FlipJumpException):
    pass


class FlipJumpExprException(FlipJumpException):
    pass


class FlipJumpAssemblerException(FlipJumpException):
    pass


class FlipJumpReadFjmException(FlipJumpException):
    pass


class FlipJumpWriteFjmException(FlipJumpException):
    pass


class FlipJumpRuntimeMemoryException(FlipJumpException):
    pass


class FlipJumpMissingImportException(FlipJumpException):
    pass

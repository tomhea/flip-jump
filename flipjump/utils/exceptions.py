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


class FlipJumpRuntimeException(FlipJumpException):
    pass


class FlipJumpRuntimeMemoryException(FlipJumpRuntimeException):
    pass


class FlipJumpMissingImportException(FlipJumpException):
    pass


class IODeviceException(IOError, FlipJumpException):
    pass


class BrokenIOUsed(IODeviceException):
    pass


class IOReadOnEOF(IODeviceException):
    pass


class IncompleteOutput(IODeviceException):
    pass

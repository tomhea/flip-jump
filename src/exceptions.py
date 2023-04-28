class FJException(Exception):
    pass


class FJParsingException(FJException):
    pass


class FJPreprocessorException(FJException):
    pass


class FJExprException(FJException):
    pass


class FJAssemblerException(FJException):
    pass


class FJReadFjmException(FJException):
    pass


class FJWriteFjmException(FJException):
    pass


class FJRuntimeMemoryException(FJException):
    pass

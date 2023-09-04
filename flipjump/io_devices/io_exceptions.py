class IODeviceException(IOError):
    pass


class BrokenIOUsed(IODeviceException):
    pass


class IOReadOnEOF(IODeviceException):
    pass


class IncompleteOutput(IODeviceException):
    pass

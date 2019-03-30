class TargetException(Exception):
    pass


class TargetNotFound(TargetException):
    pass


class TargetInternalServerError(TargetException):
    pass


class NastyTargetException(TargetException):
    pass


class TargetTimeout(TargetException):
    pass


class MalformedBodyException(TargetException):
    pass


class ValidationError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)

        self.message = message
        self.code = code

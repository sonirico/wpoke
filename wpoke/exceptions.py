class WpokeException(BaseException):
    message = ""


class TargetException(WpokeException):
    pass


class TargetConnectionError(TargetException):
    message = "Target is down or does no exist"


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


class ValidationError(WpokeException):
    def __init__(self, message, code=None):
        super().__init__(message)

        self.message = message
        self.code = code


class DuplicatedFingerException(WpokeException):
    pass


class DataStoreAttributeNotFound(AttributeError):
    pass


class ThemePathMissingException(WpokeException):
    pass


class BundledThemeException(WpokeException):
    message = (
        "The target might be using a package manager to bundle its "
        "assets, like webpack, parcel or browserify"
    )

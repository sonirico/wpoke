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


class DuplicatedFingerException(Exception):
    pass


class DataStoreAttributeNotFound(AttributeError):
    pass


class ThemePathMissingException(Exception):
    pass


class BundledThemeException(Exception):
    message = "The target might be using a package manager to bundle its " \
              "assets, like webpack, parcel or browserify"

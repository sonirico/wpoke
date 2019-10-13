class WpokeException(BaseException):
    message = ""

    def __init__(self, message="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message or self.message


class TargetException(WpokeException):
    pass


class TargetConnectionError(TargetException):
    message = "Target is down or does no exist"


class TargetNotFound(TargetException):
    message = "Target did not found an scan resource"


class TargetInternalServerError(TargetException):
    message = "Target has suffered from an internal server error"


class NastyTargetException(TargetException):
    message = (
        "Target might be detecting it's under a scan"
        " and responding with edgy behaviours"
    )


class TargetTimeout(TargetException):
    message = "Target timeout. Make sure the target payload exists"


class MalformedBodyException(TargetException):
    message = "The target site might be yielding unreadable or" " non-existent content"


class ThemePathMissingException(WpokeException):
    message = "The target might not be running Wordpress"


class BundledThemeException(WpokeException):
    message = (
        "The target might be using a package manager to bundle its "
        "assets, like webpack, parcel or browserify"
    )


# Internal exceptions


class ValidationError(WpokeException):
    def __init__(self, message, code=None):
        super().__init__(message)

        self.message = message
        self.code = code


class DuplicatedFingerException(WpokeException):
    pass


class DataStoreAttributeNotFound(AttributeError):
    pass

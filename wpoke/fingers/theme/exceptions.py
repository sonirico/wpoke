class ThemePathMissingException(Exception):
    pass


class BundledThemeException(Exception):
    message = "The target might be using a package manager to bundle its " \
              "assets, like webpack, parcel or browserify"

class FatalException(Exception):
    pass

class NonFatalException(Exception):
    pass

class NoConfigException(FatalException):
    def __init__(self, text='No config file'):
        super().__init__(text)

class InvalidConfigException(FatalException):
    def __init__(self, text='Invalid config file'):
        super().__init__(text)

class InvalidEmailException(InvalidConfigException):
    def __init__(self, email='UNSPECIFIED'):
        super().__init__(f"Invalid email: {email}")

class InvalidURLException(InvalidConfigException):
    def __init__(self, url='UNSPECIFIED'):
        super().__init__(f"Invalid URL: {url}")

class NoKeysException(InvalidConfigException):
    def __init__(self):
        super().__init__("No authentication keys")

class BadKeysException(InvalidConfigException):
    def __init__(self):
        super().__init__("Bad authentication keys")

class NoInternetException(NonFatalException):
    def __init__(self):
        super().__init__("No Internet connection")

class NoWhitelistedMessageException(NonFatalException):
    def __init__(self):
        super().__init__("No whitelisted message was found")

class NonFatalFetchException (NonFatalException):
    pass
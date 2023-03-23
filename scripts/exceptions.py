class FatalException(Exception):
    pass

class NonFatalException(Exception):
    pass

class NoConfigException(FatalException):
    def __init__(self):
        super().__init__("No config file")

class InvalidConfigException(FatalException):
    def __init__(self):
        super().__init__("Invalid config file")

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
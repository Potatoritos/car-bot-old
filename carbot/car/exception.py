__all__ = [
    'CheckError',
    'ArgumentError',
    'CommandError'
]

class CheckError(Exception):
    def __init__(self, error_msg):
        super().__init__()
        self.error_msg = error_msg

class ArgumentError(Exception):
    def __init__(self, error_msg, index=-1):
        super().__init__()
        self.error_msg = error_msg
        self.index = index

class CommandError(Exception):
    def __init__(self, error_msg, index=-1):
        super().__init__()
        self.error_msg = error_msg
        self.index = index


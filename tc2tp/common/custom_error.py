class CustomError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class IncorrectError(CustomError):
    def __init__(self, msg: str = "Incorrect Error!") -> None:
        super().__init__(msg)


class MismatchError(CustomError):
    """can not meet the requirements"""
    def __init__(self, msg: str = "Mismatch error!") -> None:
        super().__init__(msg)


class IgnoredError(CustomError):
    """error can be ignored"""
    def __init__(self, msg: str = "Ignored error!") -> None:
        super().__init__(msg)


class NullValueError(CustomError):
    """value is null"""
    def __init__(self, msg: str = "Null value error!") -> None:
        super().__init__(msg)


class InvalidParamError(CustomError):
    """parameter is invalid"""
    def __init__(self, msg: str = "Invalid parameter error!") -> None:
        super().__init__(msg)


class NotFoundError(CustomError):
    """can not find the data in database"""
    def __init__(self, msg: str = "Not found error!") -> None:
        super().__init__(msg)

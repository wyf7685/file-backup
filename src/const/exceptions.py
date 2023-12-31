from typing import Optional


class Error(Exception):
    msg: str

    def __init__(self, msg: str = "") -> None:
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.__class__.__name__} - {self.msg}"


class OperationError(Error):
    uuid: Optional[str] = None


class StopOperation(OperationError):
    pass


class RestartOperation(OperationError):
    pass


class StopBackup(StopOperation):
    pass


class RestartBackup(RestartOperation):
    pass


class StopRecovery(StopOperation):
    pass


class CommandExit(StopOperation):
    pass


class AccountError(Error):
    pass


class LoginError(AccountError):
    pass


class AccountNotLogin(LoginError):
    pass


class AccountLoginFailed(LoginError):
    pass


class RegisterFailed(AccountError):
    pass

from typing import Optional


class Error(Exception):
    """`file-backup` 所有错误类型的基类"""

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
    trace: bool

    def __init__(self, msg: str = "", trace: bool = False) -> None:
        self.msg = msg
        self.trace = trace


class BackendError(Error):
    pass

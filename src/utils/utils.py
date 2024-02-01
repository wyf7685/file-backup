import asyncio
import shutil
import sys
from contextvars import copy_context
from functools import partial, wraps
from hashlib import md5
from pathlib import Path
from sys import exc_info
from types import FrameType
from typing import Callable, Coroutine, cast
from uuid import uuid4


def get_md5(path: Path) -> str:
    if not path.is_file():
        raise ValueError("path must be a file")
    return md5(path.read_bytes()).hexdigest()


def get_uuid() -> str:
    return str(uuid4())


def mkdir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_pycache(path: Path = Path()) -> None:
    """移除指定目录下的 `__pycache__` 文件夹

    参数:
        path (Path, optional): 指定目录. 默认为当前目录
    """
    for p in path.iterdir():
        if not p.is_dir():
            continue
        if p.name == "__pycache__":
            shutil.rmtree(p)
        else:
            clean_pycache(p)


def compress_password(uuid: str) -> str:
    return md5(f"{uuid}$file-backup".encode()).hexdigest()


def run_sync[**P, R](call: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    """一个用于包装同步函数为异步函数的装饰器

    参数:
        call: 被装饰的同步函数
    """

    @wraps(call)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_running_loop()
        pfunc = partial(call, *args, **kwargs)
        context = copy_context()
        return await loop.run_in_executor(None, partial(context.run, pfunc))

    return wrapper


def _get_frame(__depth: int, /) -> FrameType:
    # sourcery skip: raise-specific-error
    try:
        raise Exception
    except Exception:
        frame = exc_info()[2].tb_frame.f_back  # type: ignore
        for _ in range(__depth):
            frame = frame.f_back  # type: ignore
        return frame  # type: ignore


get_frame = cast(Callable[[int], FrameType], getattr(sys, "_getframe", _get_frame))

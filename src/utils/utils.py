import shutil
from contextvars import copy_context
from functools import partial, wraps
from hashlib import md5
from pathlib import Path
from typing import Callable, Coroutine, ParamSpec, TypeVar
from uuid import uuid4

P = ParamSpec("P")
R = TypeVar("R")


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
        path (Path, optional): 指定目录. 默认为 Path().
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


def run_sync(call: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
    """一个用于包装 sync function 为 async function 的装饰器

    参数:
        call: 被装饰的同步函数
    """
    import asyncio

    @wraps(call)
    async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_running_loop()
        pfunc = partial(call, *args, **kwargs)
        context = copy_context()
        result = await loop.run_in_executor(None, partial(context.run, pfunc))
        return result

    return _wrapper


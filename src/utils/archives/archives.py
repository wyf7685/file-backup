import os as _os
from subprocess import Popen, PIPE
from pathlib import Path
from typing import List, Optional
import platform

from ..utils import run_sync

WINDOWS = platform.system() == "Windows"


def _init_7zip() -> str:
    if WINDOWS:
        from base64 import b64decode
        from .raw_7z import EXE_RAW, DLL_RAW

        CACHE_PATH = Path(_os.getenv("TEMP") or "data/cache")
        CACHE_PATH.mkdir(exist_ok=True, parents=True)

        exe_path = CACHE_PATH / "7z.exe"
        dll_path = CACHE_PATH / "7z.dll"

        exe_path.write_bytes(b64decode(EXE_RAW))
        dll_path.write_bytes(b64decode(DLL_RAW))
    else:
        p = Popen(["which", "7z"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, _ = p.communicate()
        if not (exe_path := output.decode().strip()):
            raise RuntimeError("7z not installed, please install p7zip-full first")

    return str(exe_path)


def _execute_7z(args: List[str]):
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    return "Everything is Ok" in (
        output.decode("gbk") if WINDOWS else output.decode()
    ) and p.returncode == 0, (err.decode("gbk") if WINDOWS else err.decode())


def _pack_7zip(archive: Path, root: Path, password: Optional[str] = None) -> Path:
    args = [EXE_PATH, "a", "-t7z", "-r", str(archive), f"{root}/*"]
    if password:
        args.insert(4, f"-p{password}")

    success, err = _execute_7z(args)
    if success:
        return archive
    raise RuntimeError(f"压缩文件错误: {err}")


def _unpack_7zip(archive: Path, target: Path, password: Optional[str] = None) -> Path:
    args = [EXE_PATH, "x", str(archive), f"-o{target}"]
    if password:
        args.insert(2, f"-p{password}")

    success, err = _execute_7z(args)
    if success:
        return archive
    raise RuntimeError(f"解压文件错误: {err}")


@run_sync
def pack_7zip(archive: Path, root: Path, password: Optional[str] = None) -> Path:
    return _pack_7zip(archive=archive, root=root, password=password)


@run_sync
def unpack_7zip(archive: Path, target: Path, password: Optional[str] = None) -> Path:
    return _unpack_7zip(archive=archive, target=target, password=password)


def _pack_7zip_multipart(
    archive: Path, root: Path, volume_size: int, password: Optional[str] = None
) -> List[Path]:
    args = [EXE_PATH, "a", "-t7z", "-r", f"-v{volume_size}m", str(archive), f"{root}/*"]
    if password:
        args.insert(5, f"-p{password}")

    success, err = _execute_7z(args)
    if success:
        return [
            p
            for p in archive.parent.iterdir()
            if p.is_file()
            and p.name.startswith(archive.name)
            and p.name.split(".")[-1].isdigit()
        ]
    raise RuntimeError(f"压缩文件错误: {err}")


@run_sync
def pack_7zip_multipart(
    archive: Path, root: Path, volume_size: int, password: Optional[str] = None
) -> List[Path]:
    return _pack_7zip_multipart(archive, root, volume_size, password)


EXE_PATH = _init_7zip()

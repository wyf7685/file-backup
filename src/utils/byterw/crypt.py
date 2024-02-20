import base64
import ctypes
import functools
import random
import string
from pathlib import Path
import typing

LIB_PATH = str(Path.cwd() / "lib/crypt.dll")
LIB = ctypes.CDLL(LIB_PATH)

lib_encrypt = LIB.encrypt
lib_encrypt.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_uint64,
]
lib_encrypt.restype = ctypes.POINTER(ctypes.c_ubyte)

lib_decrypt = LIB.decrypt
lib_decrypt.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_uint64,
]
lib_decrypt.restype = ctypes.POINTER(ctypes.c_ubyte)

lib_free = LIB.myfree
lib_free.argtypes = [ctypes.c_void_p]
lib_free.restype = None


def _process(
    lib_call: typing.Callable[[bytes, ctypes.Array[ctypes.c_ubyte], int], typing.Any],
    charset: str,
    data: bytes | bytearray,
):
    d = (ctypes.c_ubyte * len(data))(*data)
    ptr = lib_call(charset.encode("utf-8"), d, len(data))
    result = bytes(
        ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte * len(data))).contents
    )
    lib_free(ptr)
    return result


@functools.cache
def get_charset(key: str | int) -> str:
    m = list(string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/")
    random.Random(key).shuffle(m)
    return "".join(m) + "="


def encrypt(data: bytes | bytearray, key: str | int | None = None) -> bytes:
    b64 = base64.b64encode(data)
    charset = get_charset(key or 7685)
    return _process(lib_encrypt, charset, b64)

def decrypt(data: bytes | bytearray, key: str | int | None = None) -> bytes:
    charset = get_charset(key or 7685)
    b64 = _process(lib_decrypt, charset, data)
    return base64.b64decode(b64)

import base64
import ctypes
import functools
import random
import string
import sys
from pathlib import Path


class CLib:
    def __init__(self):
        LIB_NAME = f"crypt.{"dll" if sys.platform == "win32" else "so"}"
        LIB_PATH = Path.cwd() / "lib" / LIB_NAME
        self.LIB = ctypes.CDLL(str(LIB_PATH))

        self.lib_encrypt = self.LIB.encrypt
        self.lib_encrypt.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint64,
        ]
        self.lib_encrypt.restype = ctypes.POINTER(ctypes.c_ubyte)

        self.lib_decrypt = self.LIB.decrypt
        self.lib_decrypt.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint64,
        ]
        self.lib_decrypt.restype = ctypes.POINTER(ctypes.c_ubyte)

        self.lib_free = self.LIB.myfree
        self.lib_free.argtypes = [ctypes.c_void_p]
        self.lib_free.restype = None

    def _process(self, f: bool, charset: str, data: bytes | bytearray) -> bytes:
        d = (ctypes.c_ubyte * len(data))(*data)
        call = self.lib_encrypt if f else self.lib_decrypt
        ptr = call(charset.encode("utf-8"), d, len(data))
        result = bytes(
            ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte * len(data))).contents
        )
        self.lib_free(ptr)
        return result

    def encrypt(self, charset: str, data: bytes | bytearray) -> bytes:
        return self._process(True, charset, data)

    def decrypt(self, charset: str, data: bytes | bytearray) -> bytes:
        return self._process(False, charset, data)


CLIB = CLib()


@functools.cache
def get_charset(key: str | int | None = None) -> str:
    if key is None:
        key = 7685
    m = list(string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/")
    random.Random(key).shuffle(m)
    return "".join(m) + "="


def encrypt(data: bytes | bytearray, key: str | int | None = None) -> bytes:
    return CLIB.encrypt(get_charset(key), base64.b64encode(data))


def decrypt(data: bytes | bytearray, key: str | int | None = None) -> bytes:
    return base64.b64decode(CLIB.decrypt(get_charset(key), data))

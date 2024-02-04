import base64
import random
import string

__basic_map = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/="


def __get_map(key: str | int) -> str:
    m = list(__basic_map[:-1])
    random.Random(key).shuffle(m)
    return "".join(m) + "="


def __offset(data: bytes | bytearray, offset: int) -> bytes:
    buffer = bytearray(data)
    for i in range(len(buffer)):
        buffer[i] = (buffer[i] + offset) % 256
    return bytes(buffer)


def encrypt(data: bytes | bytearray, key: str | int | None = None) -> bytes:
    mapping = __get_map(key or 7685)
    b64 = base64.b64encode(data).decode("utf-8")
    b64 = "".join(mapping[__basic_map.index(i)] for i in b64)
    return __offset(b64.encode("utf-8"), -7685)


def decrypt(b64b: bytes | bytearray, key: str | int | None = None) -> bytes:
    mapping = __get_map(key or 7685)
    b64 = __offset(b64b, 7685).decode("utf-8")
    b64 = "".join(__basic_map[mapping.index(i)] for i in b64)
    return base64.b64decode(b64)

__b64_mapping = "+wDKPW3FRpjvoSG5ECQgJiUVsybaIcX8u/zxltdZL1920qBfheTnA7YHmO4NMk6r"


def __offset(data: bytes, offset: int) -> bytes:
    buffer = bytearray(data)
    for i in range(len(buffer)):
        buffer[i] = (buffer[i] + offset) % 256
    return bytes(buffer)


def encrypt(data: bytes) -> bytes:
    padding = (3 - len(data) % 3) % 3
    data += b"\x00" * padding
    b64 = ""

    for i in range(0, len(data), 3):
        chunk = (data[i] << 16) + (data[i + 1] << 8) + data[i + 2]
        for j in range(4):
            b64 += __b64_mapping[(chunk >> (18 - j * 6)) & 0x3F]

    if padding:
        b64 = b64[:-padding] + "=" * padding

    return __offset(b64.encode("utf-8"), -7685)


def decrypt(b64b: bytes) -> bytes:
    b64 = __offset(b64b, 7685).decode("utf-8").replace("=", "")
    bs = "".join(format(__b64_mapping.index(char), "06b") for char in b64)

    data = bytearray()
    for i in range(0, len(bs), 8):
        data.append(int(bs[i : i + 8], 2))

    return bytes(data)

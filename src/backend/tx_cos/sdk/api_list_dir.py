from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple

from .config import ROOT


def list_dir(path: str) -> List[Tuple[Literal["d", "f"], str]]:
    from .config import client, bucket

    prefix = f"{(ROOT / path).as_posix()}/"
    prefix_p = Path(prefix)
    marker = ""
    result: List[Tuple[Literal["d", "f"], str]] = []

    while marker is not None:
        response: Dict[str, Any] = client.list_objects(bucket, prefix, "/", marker)  # type: ignore

        result.extend(
            ("d", Path(d["Prefix"]).relative_to(prefix_p).as_posix())
            for d in response.get("CommonPrefixes", [])
        )
        result.extend(
            ("f", Path(f["Key"]).relative_to(prefix_p).as_posix())
            for f in response.get("Contents", [])
            if f["Key"] != prefix
        )
        marker = response.get("NextMarker")

    return sorted(result)

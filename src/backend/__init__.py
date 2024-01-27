import typing as _t

from .backend import AbstractBackend as Backend


def get_backend(name: _t.Optional[str] = None) -> _t.Type[Backend]:
    from importlib import import_module

    from .config import config

    name = name or config.type
    if name in {"backend", "backend_cmd", "config"}:
        raise ValueError(f"不存在名为 {name} 的 Backend")

    try:
        module = import_module(f".{name}", __package__)
    except ImportError as err:
        raise ValueError(f"不存在名为 {name} 的 Backend") from err

    backend_cls = getattr(module, "Backend", Backend)
    assert issubclass(backend_cls, Backend)
    return backend_cls

import typing as _t

from .backend import BaseBackend as Backend


def get_backend() -> _t.Type[Backend]:
    from importlib import import_module

    from .config import config

    module = import_module(f".{config.type}", __package__)
    backend_cls = getattr(module, "Backend", Backend)
    assert issubclass(backend_cls, Backend)
    return backend_cls

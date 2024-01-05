import typing as _t
from .backend import Backend as Backend


def get_backend() -> _t.Type[Backend]:
    from importlib import import_module
    from src.models import config

    module = import_module("." + config.backend.type, __package__)
    backend_cls = getattr(module, "Backend", Backend)
    assert issubclass(backend_cls, Backend)
    return backend_cls

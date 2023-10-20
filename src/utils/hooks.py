from dataclasses import dataclass
from base64 import b64encode, b64decode
from collections import defaultdict
from functools import wraps
from types import FunctionType, MethodType
from typing import Any, Callable, DefaultDict, Dict, List, ParamSpec, TypeVar

HookPoint = {}  # type: Dict[str, Callable]
BeforeHookFunc = defaultdict(list)  # type: DefaultDict[str, List[Callable]]
AfterHookFunc = defaultdict(list)  # type: DefaultDict[str, List[Callable]]

_P = ParamSpec("_P")
_T = TypeVar("_T")


@dataclass
class BeforeHookArg(object):
    args: list
    kwargs: dict


@dataclass
class AfterHookRes(object):
    res: Any


def _callBeforeHook(name: str, args: BeforeHookArg) -> None:
    for hook in BeforeHookFunc[name]:
        try:
            hook(args)
        except Exception as e:
            print(
                f"Error occured in before hook: {name}",
                f"\tHookFunc: {hook}",
                f"\tHook args: {args}",
                f"\tException: {e}",
                sep="\n",
                end="\n",
            )


def _callAfterHook(name: str, res: AfterHookRes) -> None:
    for hook in AfterHookFunc[name]:
        try:
            hook(res)
        except Exception as e:
            print(
                f"Error occured in before hook: {name}",
                f"\tHookFunc: {hook}",
                f"\tHook args: {res}",
                f"\tException: {e}",
                sep="\n",
                end="\n",
            )


def regHookPoint(name: str) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    assert name not in HookPoint, f"HookPoint {name} already exists"

    def decorator(func: Callable[_P, _T]) -> Callable[_P, _T]:
        HookPoint[name] = func

        @wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            if name not in HookPoint or not callable(HookPoint[name]):
                return func(*args, **kwargs)
            hookargs = BeforeHookArg(args=list(args), kwargs=kwargs)
            _callBeforeHook(name, hookargs)
            try:
                res = HookPoint[name](*hookargs.args, **hookargs.kwargs)
            except Exception as e:
                raise e
            else:
                hookres = AfterHookRes(res=res)
                _callAfterHook(name, hookres)
                return hookres.res

        return wrapper

    return decorator


def _regHookToken(type: str, name: str, func: Callable) -> str:
    return b64encode(f"{type}${name}${id(func)}".encode()).decode()


def regBeforeHook(name: str) -> Callable[[Callable[_P, Any]], str]:
    def decorator(func: Callable[_P, Any]) -> str:
        BeforeHookFunc[name].append(func)
        return _regHookToken("before", name, func)

    return decorator


def regAfterHook(name: str) -> Callable[[Callable[_P, Any]], str]:
    def decorator(func: Callable[_P, Any]) -> str:
        AfterHookFunc[name].append(func)
        return _regHookToken("after", name, func)

    return decorator


def unregHook(token: str):
    err = f"invalid reg token: {token}"

    data = b64decode(token).decode().split("$")
    assert len(data) == 3, err

    mode, name, func_id = data
    assert mode in {"before", "after"}, err

    func_dict = BeforeHookFunc if mode == "before" else AfterHookFunc
    assert name in func_dict, err

    assert func_id.isdigit(), err
    func_id = int(func_id)

    funcl = [func for func in func_dict[name] if id(func) == func_id]
    assert len(funcl), err

    func_dict[name].remove(funcl.pop(0))


def hookable(obj: _T) -> _T:
    assert isinstance(obj, (type, FunctionType, MethodType))

    if isinstance(obj, type):
        for name in dir(obj):
            attr = getattr(obj, name)
            if isinstance(attr, (FunctionType, MethodType)):
                setattr(obj, name, regHookPoint(f"{obj.__name__}.{name}")(attr))
    else:
        obj = regHookPoint(obj.__name__)(obj)

    return obj

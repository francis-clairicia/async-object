# -*- coding: Utf-8 -*-
# Copyright (c) 2023, Francis Clairicia-Rose-Claire-Josephine
#
#
"""async-object let you write classes with async def __init__.

async-object defines an AsyncObject base class which uses async constructors.
"""

from __future__ import annotations

__all__ = ["AsyncABC", "AsyncABCMeta", "AsyncObject", "AsyncObjectMeta"]

__author__ = "FrankySnow9"
__contact__ = "clairicia.rcj.francis@gmail.com"
__copyright__ = "Copyright (c) 2023, Francis Clairicia-Rose-Claire-Josephine"
__credits__ = ["FrankySnow9"]
__deprecated__ = False
__email__ = "clairicia.rcj.francis@gmail.com"
__license__ = "MIT"
__maintainer__ = "FrankySnow9"
__status__ = "Production"
__version__ = "2.0.0"

import abc
import inspect
from functools import partialmethod
from typing import TYPE_CHECKING, Any, Callable, TypeVar


def _validate_constructor(func: Any, name: str) -> None:
    if isinstance(func, partialmethod):  # pragma: no cover
        return _validate_constructor(func.func, name)

    if not inspect.iscoroutinefunction(func):
        raise TypeError(f"{name!r} must be a coroutine function (using 'async def')")


class AsyncObjectMeta(type):
    if TYPE_CHECKING:
        __Self = TypeVar("__Self", bound="AsyncObjectMeta")

    def __new__(mcs: type[__Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwargs: Any) -> __Self:
        for attr in {"__init__"}:
            try:
                func = namespace[attr]
            except KeyError:
                continue
            _validate_constructor(func, attr)

        try:
            absolute_base_class = AsyncObject
        except NameError:  # pragma: no cover
            if name == "AsyncObject" and namespace.get("__module__") == __name__:
                return super().__new__(mcs, name, bases, namespace, **kwargs)
            raise

        if "__await__" in namespace:
            raise TypeError("AsyncObject subclasses must not have __await__ method")

        if not any(issubclass(b, absolute_base_class) for b in bases):
            raise TypeError(f"{name} must explicitly derive from {absolute_base_class.__name__}")
        if invalid_bases := [
            b.__name__ for b in bases if not issubclass(b, absolute_base_class) and (b.__init__ is not object.__init__)
        ]:
            raise TypeError(f"These non-async base classes define a custom __init__: {', '.join(map(repr, invalid_bases))}")
        if invalid_bases := [b.__name__ for b in bases if hasattr(b, "__await__")]:
            raise TypeError(f"These base classes define __await__: {', '.join(map(repr, invalid_bases))}")
        return super().__new__(mcs, name, bases, namespace, **kwargs)

    def __setattr__(cls, name: str, value: Any, /) -> None:
        if cls is AsyncObject:
            raise AttributeError("AsyncObject is immutable")
        if name == "__await__":
            raise TypeError("AsyncObject subclasses must not have __await__ method")
        if name == "__init__":
            _validate_constructor(value, name)
        return super().__setattr__(name, value)

    def __delattr__(cls, name: str, /) -> None:
        if cls is AsyncObject:
            raise AttributeError("AsyncObject is immutable")
        if name in {"__await__", "__init__"}:
            raise TypeError(f"{name}() cannot be deleted")
        return super().__delattr__(name)

    async def __call__(cls, /, *args: Any, **kwargs: Any) -> Any:
        cls_new: Callable[..., Any] = cls.__new__
        if cls_new is object.__new__:
            self = cls_new(cls)
        else:
            self = cls_new(cls, *args, **kwargs)
        cls_init = type(self).__init__
        if cls_init is not AsyncObject.__init__ or cls_new is object.__new__:
            await cls_init(self, *args, **kwargs)
        return self


class AsyncObject(metaclass=AsyncObjectMeta):
    __slots__ = ()

    async def __init__(self) -> None:  # type: ignore[misc]
        pass


class AsyncABCMeta(AsyncObjectMeta, abc.ABCMeta):
    pass


class AsyncABC(AsyncObject, metaclass=AsyncABCMeta):
    __slots__ = ()

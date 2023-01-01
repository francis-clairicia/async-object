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
__version__ = "1.0.0rc0"

import abc
import inspect
from functools import partialmethod
from typing import TYPE_CHECKING, Any, Callable, Generator, TypeVar


class AsyncObjectMeta(type):
    if TYPE_CHECKING:
        __Self = TypeVar("__Self", bound="AsyncObjectMeta")

    def __new__(mcs: type[__Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwargs: Any) -> __Self:
        for attr in {"__new__", "__init__"}:
            try:
                func = namespace[attr]
            except KeyError:
                continue
            if isinstance(func, (staticmethod, classmethod)):
                func = func.__func__
            elif isinstance(func, partialmethod):
                func = func.func
            if not inspect.iscoroutinefunction(func):
                raise TypeError(f"{attr!r} must be a coroutine function (using 'async def')")

        try:
            absolute_base_class = AsyncObject
        except NameError:  # pragma: no cover
            if name == "AsyncObject" and namespace.get("__module__") == __name__:
                return super().__new__(mcs, name, bases, namespace, **kwargs)
            raise

        if "__await__" in namespace:
            raise TypeError("__await__() cannot be overriden")

        if not bases or any(not issubclass(b, absolute_base_class) for b in bases):
            raise TypeError(f"All base classes must be a subclass of {absolute_base_class.__name__}")

        return super().__new__(mcs, name, bases, namespace, **kwargs)

    def __setattr__(cls, name: str, value: Any, /) -> None:
        if cls is AsyncObject:
            raise AttributeError("AsyncObject is immutable")
        if name == "__await__":
            raise TypeError("__await__() cannot be overriden")
        if name in {"__new__", "__init__"}:
            if not inspect.iscoroutinefunction(value):
                raise TypeError(f"{name!r} must be a coroutine function (using 'async def')")
        return super().__setattr__(name, value)

    def __delattr__(cls, name: str, /) -> None:
        if cls is AsyncObject:
            raise AttributeError("AsyncObject is immutable")
        if name in {"__await__", "__new__", "__init__"}:
            raise TypeError(f"{name}() cannot be deleted")
        return super().__delattr__(name)

    async def __call__(cls, /, *args: Any, **kwargs: Any) -> Any:
        cls_new: Callable[..., Any] = cls.__new__
        if cls_new is AsyncObject.__new__:
            self = await cls_new(cls)
        else:
            self = await cls_new(cls, *args, **kwargs)
        cls_init = type(self).__init__
        if cls_init is not AsyncObject.__init__ or cls_new is AsyncObject.__new__:
            await cls_init(self, *args, **kwargs)
        return self


class AsyncObject(metaclass=AsyncObjectMeta):
    __slots__ = ()

    if TYPE_CHECKING:
        __Self = TypeVar("__Self", bound="AsyncObject")

    async def __new__(cls: type[__Self]) -> __Self:  # type: ignore[misc]
        return object.__new__(cls)

    async def __init__(self) -> None:  # type: ignore[misc]
        pass

    if TYPE_CHECKING:

        # Static type checkers like mypy think 'await AsyncObject()' is
        # 'await instanciated object'
        def __await__(self: __Self) -> Generator[Any, None, __Self]:
            ...


class AsyncABCMeta(AsyncObjectMeta, abc.ABCMeta):
    pass


class AsyncABC(AsyncObject, metaclass=AsyncABCMeta):
    __slots__ = ()

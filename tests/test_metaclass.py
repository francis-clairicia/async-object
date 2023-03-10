# -*- coding: Utf-8 -*-

from __future__ import annotations

import abc
import inspect
from typing import Any, Generator

import pytest

from async_object import AsyncABC, AsyncABCMeta, AsyncObject, AsyncObjectMeta


def test_no_base_class() -> None:
    with pytest.raises(TypeError, match=r"^_ must explicitly derive from AsyncObject$"):

        class _(metaclass=AsyncObjectMeta):
            pass


def test_non_async_base_class() -> None:
    class A:
        pass

    class _(A, AsyncObject):
        pass


def test_non_async_base_class_with_custom_dunder_new_or_dunder_init() -> None:
    with pytest.raises(TypeError, match=r"^These non-async base classes defines a custom __new__ or __init__: 'A', 'B'$"):

        class A:
            def __new__(cls) -> Any:
                pass

        class B:
            def __init__(self) -> None:
                pass

        class _(AsyncObject, A, B):
            pass


def test_dunder_init_not_a_coroutine_function() -> None:
    with pytest.raises(TypeError, match=r"^'__init__' must be a coroutine function \(using 'async def'\)$"):

        class _(AsyncObject):
            def __init__(self) -> None:
                ...


def test_dunder_new_not_a_coroutine_function() -> None:
    with pytest.raises(TypeError, match=r"^'__new__' must be a coroutine function \(using 'async def'\)$"):

        class _(AsyncObject):
            def __new__(cls) -> Any:
                ...


def test_dunder_await_defined() -> None:
    with pytest.raises(TypeError, match=r"^__await__\(\) cannot be overriden$"):

        class _(AsyncObject):
            def __await__(self) -> Generator[Any, None, Any]:
                return super().__await__()


def test_AsyncObject_immutable_on_set() -> None:
    with pytest.raises(AttributeError, match=r"^AsyncObject is immutable$"):
        setattr(AsyncObject, "something", None)


def test_AsyncObject_immutable_on_delete() -> None:
    with pytest.raises(AttributeError, match=r"^AsyncObject is immutable$"):
        delattr(AsyncObject, "something")


@pytest.mark.parametrize("attr", ["__new__", "__init__"])
def test_dunder_init_overwritable_with_another_coroutine(attr: str) -> None:
    async def __new_func__(self: Any) -> None:
        pass

    class MyObject(AsyncObject):
        pass

    setattr(MyObject, attr, __new_func__)

    assert getattr(MyObject, attr) is __new_func__


@pytest.mark.parametrize("attr", ["__new__", "__init__"])
def test_constructor_overwrite_error(attr: str) -> None:
    def __new_func__(self: Any) -> None:
        pass

    class MyObject(AsyncObject):
        pass

    with pytest.raises(TypeError, match=r"^{!r} must be a coroutine function \(using 'async def'\)$".format(attr)):
        setattr(MyObject, attr, __new_func__)


def test_setattr_something_else() -> None:
    class MyObject(AsyncObject):
        pass

    setattr(MyObject, "_custom_attr", 123456)

    assert getattr(MyObject, "_custom_attr") == 123456


def test_dunder_await_set() -> None:
    class MyObject(AsyncObject):
        pass

    with pytest.raises(TypeError, match=r"^__await__\(\) cannot be overriden$"):
        MyObject.__await__ = None  # type: ignore[assignment]


@pytest.mark.parametrize("attr", ["__await__", "__new__", "__init__"])
def test_attribute_cannot_be_deleted(attr: str) -> None:
    class MyObject(AsyncObject):
        pass

    with pytest.raises(TypeError, match=r"^{}\(\) cannot be deleted$".format(attr)):
        delattr(MyObject, attr)


def test_delattr_something_else() -> None:
    class MyObject(AsyncObject):
        pass

    setattr(MyObject, "_custom_attr", 123456)

    delattr(MyObject, "_custom_attr")

    assert not hasattr(MyObject, "_custom_attr")


@pytest.mark.asyncio
async def test_abc_meta() -> None:
    class AbstractAsyncObject(AsyncObject, metaclass=AsyncABCMeta):
        @abc.abstractmethod
        def method(self) -> None:
            pass

        @abc.abstractmethod
        async def async_method(self) -> None:
            pass

    assert inspect.isabstract(AbstractAsyncObject)
    assert AbstractAsyncObject.__abstractmethods__ == frozenset({"method", "async_method"})

    class AsyncObjectImpl(AbstractAsyncObject):
        def method(self) -> None:
            pass

        async def async_method(self) -> None:
            pass

    instance = await AsyncObjectImpl()

    assert isinstance(instance, AsyncObjectImpl)


@pytest.mark.asyncio
async def test_abc_base_class_shorthand() -> None:
    class AbstractAsyncObject(AsyncABC):
        @abc.abstractmethod
        def method(self) -> None:
            pass

        @abc.abstractmethod
        async def async_method(self) -> None:
            pass

    assert inspect.isabstract(AbstractAsyncObject)
    assert AbstractAsyncObject.__abstractmethods__ == frozenset({"method", "async_method"})

    class AsyncObjectImpl(AbstractAsyncObject):
        def method(self) -> None:
            pass

        async def async_method(self) -> None:
            pass

    instance = await AsyncObjectImpl()

    assert isinstance(instance, AsyncObjectImpl)

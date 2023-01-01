# -*- coding: Utf-8 -*-

from __future__ import annotations

from typing import Any, Generator

import pytest

from async_object import AsyncObject, AsyncObjectMeta


def test_no_base_class() -> None:
    with pytest.raises(TypeError, match=r"All base classes must be a subclass of AsyncObject"):

        class _(metaclass=AsyncObjectMeta):
            pass


def test_non_async_base_classes() -> None:
    with pytest.raises(TypeError, match=r"All base classes must be a subclass of AsyncObject"):

        class A:
            pass

        class _(A, AsyncObject):
            pass


def test_dunder_init_not_a_coroutine_function() -> None:
    with pytest.raises(TypeError, match=r"'__init__' must be a coroutine function \(using 'async def'\)"):

        class _(AsyncObject):
            def __init__(self) -> None:
                ...


def test_dunder_await_defined() -> None:
    with pytest.raises(TypeError, match=r"__await__\(\) cannot be overriden"):

        class _(AsyncObject):
            def __await__(self) -> Generator[Any, None, Any]:
                return super().__await__()


def test_AsyncObject_immutable_on_set() -> None:
    with pytest.raises(AttributeError, match=r"AsyncObject is immutable"):
        setattr(AsyncObject, "something", None)


def test_AsyncObject_immutable_on_delete() -> None:
    with pytest.raises(AttributeError, match=r"AsyncObject is immutable"):
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

    with pytest.raises(TypeError, match=r"{!r} must be a coroutine function \(using 'async def'\)".format(attr)):
        setattr(MyObject, attr, __new_func__)


def test_setattr_something_else() -> None:
    class MyObject(AsyncObject):
        pass

    setattr(MyObject, "_custom_attr", 123456)

    assert getattr(MyObject, "_custom_attr") == 123456


def test_dunder_await_set() -> None:
    class MyObject(AsyncObject):
        pass

    with pytest.raises(TypeError, match=r"__await__\(\) cannot be overriden"):
        MyObject.__await__ = None  # type: ignore[assignment]


@pytest.mark.parametrize("attr", ["__await__", "__new__", "__init__"])
def test_attribute_cannot_be_deleted(attr: str) -> None:
    class MyObject(AsyncObject):
        pass

    with pytest.raises(TypeError, match=r"{}\(\) cannot be deleted".format(attr)):
        delattr(MyObject, attr)


def test_delattr_something_else() -> None:
    class MyObject(AsyncObject):
        pass

    setattr(MyObject, "_custom_attr", 123456)

    delattr(MyObject, "_custom_attr")

    assert not hasattr(MyObject, "_custom_attr")

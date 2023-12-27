# -*- coding: Utf-8 -*-

from __future__ import annotations

import pytest
from typing_extensions import Self

from async_object import AsyncObject

pytestmark = pytest.mark.asyncio


async def test_simple_instanciation() -> None:
    # Arrange

    # Act
    instance: AsyncObject = await AsyncObject()

    # Assert
    assert isinstance(instance, AsyncObject)


async def test_subclass() -> None:
    # Arrange

    class MyObject(AsyncObject):
        async def __init__(self) -> None:
            await super().__init__()
            self.myattr_from_init: int = 2

    # Act
    instance: MyObject = await MyObject()

    # Assert
    assert isinstance(instance, MyObject)
    assert instance.myattr_from_init == 2


async def test_subclass_with_arguments() -> None:
    # Arrange

    class MyObject(AsyncObject):
        async def __init__(self, value: int) -> None:
            await super().__init__()
            self.myattr_from_init: int = value

    # Act
    instance: MyObject = await MyObject(value=123456789)

    # Assert
    assert isinstance(instance, MyObject)
    assert instance.myattr_from_init == 123456789


async def test_subclass_with_arguments_for_dunder_new() -> None:
    # Arrange

    class MyObject(AsyncObject):
        myattr_from_new: int

        def __new__(cls, value: int) -> Self:
            self = super().__new__(cls)
            self.myattr_from_new = value
            return self

    # Act
    instance: MyObject = await MyObject(value=123456789)

    # Assert
    assert isinstance(instance, MyObject)
    assert instance.myattr_from_new == 123456789


async def test_subclass_with_custom_dunder_new() -> None:
    # Arrange

    class MyObject(AsyncObject):
        def __new__(cls, value: int) -> Self:
            self = super().__new__(cls)
            self.myattr_from_new = value * 2
            return self

        async def __init__(self, value: int) -> None:
            await super().__init__()
            self.myattr_from_new: int
            self.myattr_from_init: int = value

    # Act
    instance: MyObject = await MyObject(value=123456789)

    # Assert
    assert isinstance(instance, MyObject)
    assert instance.myattr_from_new == 123456789 * 2
    assert instance.myattr_from_init == 123456789

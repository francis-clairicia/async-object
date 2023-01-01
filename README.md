# async-object
`async-object` let you write classes with `async def __init__`

## Usage
It is simple, with `async-object` you can do this :
```py
from async_object import AsyncObject


class MyObject(AsyncObject):
    async def __new__(cls) -> "MyObject":
        self = await super().__new__(cls)

        # Do some async stuff

        return self

    async def __init__(self) -> None:
        await super().__init__()

        # Do some async stuff


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        instance = await MyObject()
        assert isinstance(instance, MyObject)

    asyncio.run(main())
```

### Abstract base classes
```py
import abc

from async_object import AsyncObject, AsyncABCMeta


class MyAbstractObject(AsyncObject, metaclass=AsyncABCMeta):
    @abc.abstractmethod
    def method(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def async_method(self) -> None:
        raise NotImplementedError


class MyObject(MyAbstractObject):
    async def __init__(self, arg1: int, arg2: str) -> None:
        await super().__init__()

    def method(self) -> None:
        pass

    async def async_method(self) -> None:
        pass
```

## Troubleshoots

### Static type checking

Static type checker like `mypy` does not like having `async def` for `__new__` and `__init__`. You can use `# type: ignore[misc]` comment to mask these errors when overriding these methods.
```py
class MyObject(AsyncObject):
    async def __new__(cls) -> "MyObject":  # type: ignore[misc]
        return await super().__new__(cls)

    async def __init__(self) -> None:  # type: ignore[misc]
        await super().__init__()
```

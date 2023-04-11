# async-object
[![Test](https://github.com/francis-clairicia/async-object/actions/workflows/test.yml/badge.svg)](https://github.com/francis-clairicia/async-object/actions/workflows/test.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/francis-clairicia/async-object/main.svg)](https://results.pre-commit.ci/latest/github/francis-clairicia/async-object/main)

[![PyPI](https://img.shields.io/pypi/v/async-object)](https://pypi.org/project/async-object/)
[![PyPI - License](https://img.shields.io/pypi/l/async-object)](https://github.com/francis-clairicia/async-object/blob/main/LICENSE)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/async-object)

[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

`async-object` let you write classes with `async def __init__`

## Usage
It is simple, with `async-object` you can do this:
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

This example uses `asyncio`, but it is compatible with all runner libraries, since this package only uses the language syntax.

## Description
`async-object` provides a base class `AsyncObject` using `AsyncObjectMeta` metaclass.

`AsyncObjectMeta` overrides the default `type` constructor in order to return a coroutine, which must be `await`-ed to get the instance.

```py
async def main() -> None:
    coroutine = MyObject()
    print(coroutine)
    instance = await coroutine
    print(instance)
```

Replace the `main` in the [Usage](#usage) example by this one and run it. You should see something like this in your console:
```
<coroutine object AsyncObjectMeta.__call__ at 0x7ff1f28eb300>
<__main__.MyObject object at 0x7ff1f21a4fd0>
```

### Arguments
Obviously, arguments can be given to `__init__` and `__new__`.
The inheritance logic with "normal" constructors is the same here:
```py
class MyObjectOnlyNew(AsyncObject):
    async def __new__(cls, *args: Any, **kwargs: Any) -> "MyObject":
        self = await super().__new__(cls)

        print(args)
        print(kwargs)

        return self


class MyObjectOnlyInit(AsyncObject):
    async def __init__(self, *args: Any, **kwargs: Any) -> None:
        await super().__init__()

        print(args)
        print(kwargs)


class MyObjectBothNewAndInit(AsyncObject):
    async def __new__(cls, *args: Any, **kwargs: Any) -> "MyObject":
        self = await super().__new__(cls)

        print(args)
        print(kwargs)

        return self

    async def __init__(self, *args: Any, **kwargs: Any) -> None:
        await super().__init__()

        print(args)
        print(kwargs)
```

### Inheritance
Talking about inheritance, there are a few rules to follow:
- `AsyncObject` or a subclass must appear at least once in the base classes declaration.
- Non-`AsyncObject` classes can be used as base classes if they do not override `__new__` or `__init__` (in order not to break the [MRO](https://docs.python.org/3/glossary.html#term-method-resolution-order)).
- To avoid confusion with [awaitable objects](https://docs.python.org/3/glossary.html#term-awaitable), overriding `__await__` is forbidden.

### Abstract base classes
There is a metaclass `AsyncABCMeta` deriving from `AsyncObjectMeta` and `abc.ABCMeta` which allows you to declare abstract base classes
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
    async def __init__(self) -> None:
        await super().__init__()

    def method(self) -> None:
        pass

    async def async_method(self) -> None:
        pass
```

N.B.: There is a shorthand `AsyncABC` like `abc.ABC`.
```py
import abc

from async_object import AsyncABC


class MyAbstractObject(AsyncABC):
    @abc.abstractmethod
    def method(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def async_method(self) -> None:
        raise NotImplementedError
```

## Troubleshoots

### Static type checking

`mypy` does not like having `async def` for `__new__` and `__init__`. You can use `# type: ignore[misc]` comment to mask these errors when overriding these methods.
```py
class MyObject(AsyncObject):
    async def __new__(cls) -> "MyObject":  # type: ignore[misc]
        return await super().__new__(cls)

    async def __init__(self) -> None:  # type: ignore[misc]
        await super().__init__()
```

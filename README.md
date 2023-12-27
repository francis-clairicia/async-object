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

## Installation
### From PyPI repository
```sh
pip install --user async-object
```

### From source
```sh
git clone https://github.com/francis-clairicia/async-object.git
cd async-object
pip install --user .
```

## Usage
It is simple, with `async-object` you can do this:
```py
from async_object import AsyncObject


class MyObject(AsyncObject):
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
from typing_extensions import Self

class MyObjectOnlyNew(AsyncObject):
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        self = super().__new__(cls)

        print(args)
        print(kwargs)

        return self


class MyObjectOnlyInit(AsyncObject):
    async def __init__(self, *args: Any, **kwargs: Any) -> None:
        # await super().__init__()  # Optional if the base class is only AsyncObject (but useful in multiple inheritance context)

        print(args)
        print(kwargs)


class MyObjectBothNewAndInit(AsyncObject):
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        self = super().__new__(cls)

        print(args)
        print(kwargs)

        return self

    async def __init__(self, *args: Any, **kwargs: Any) -> None:
        # await super().__init__()

        print(args)
        print(kwargs)
```

### Inheritance
Talking about inheritance, there are a few rules to follow:
- `AsyncObject` or a subclass must appear at least once in the base classes declaration.
- Non-`AsyncObject` classes can be used as base classes if they do not override `__init__` (in order not to break the [MRO](https://docs.python.org/3/glossary.html#term-method-resolution-order)).
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
        pass

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

## Static type checking: mypy integration
`mypy` does not like having `async def` for `__init__`, and will not understand `await AsyncObject()`.

`async-object` embeds a plugin which helps `mypy` to understand asynchronous constructors.

### Installation
Firstly, install the needed dependencies:
```sh
pip install async-object[mypy]
```

To register this plugin in your `mypy.ini`, `pyproject.toml`, or whatever, you must add `async_object.contrib.mypy.plugin` to the plugins list.

In `mypy.ini`:
```ini
[mypy]
plugins = async_object.contrib.mypy.plugin
```

In `pyproject.toml`:
```toml
[tool.mypy]
plugins = ["async_object.contrib.mypy.plugin"]
```

For more information, see [the mypy documentation](https://mypy.readthedocs.io/en/stable/extending_mypy.html#configuring-mypy-to-use-plugins).

### What is permitted then ?
#### `__init__` method returning a coroutine is accepted
The error `The return type of "__init__" must be None` is discarded.
```py
class MyObject(AsyncObject):
    async def __init__(self, param: int) -> None:
        await super().__init__()
```

#### The class instanciation introspection is fixed
```py
async def main() -> None:
    coroutine = MyObject()
    reveal_type(coroutine)  # Revealed type is "typing.Coroutine[Any, Any, __main__.MyObject]"
    instance = await coroutine
    reveal_type(instance)  # Revealed type is "__main__.MyObject"
```

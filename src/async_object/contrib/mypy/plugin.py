# -*- coding: Utf-8 -*-
# Copyright (c) 2023, Francis Clairicia-Rose-Claire-Josephine
#
#
"""mypy plugin for async-object package.

This module helps mypy to understand asynchronous constructors.

To register this plugin in your mypy.ini, pyproject.toml, or whatever,
you must add "async_object.contrib.mypy.plugin" to the plugins list.

See how to register a plugin here: https://mypy.readthedocs.io/en/stable/extending_mypy.html#configuring-mypy-to-use-plugins
"""

from __future__ import annotations

__all__ = []  # type: list[str]

import importlib.util
from typing import Callable, Sequence

from mypy import errorcodes
from mypy.nodes import Decorator, FuncDef, OverloadedFuncDef, SymbolNode, SymbolTableNode, TypeInfo
from mypy.plugin import ClassDefContext, FunctionContext, Plugin
from mypy.types import AnyType, Type, TypeOfAny

_ASYNC_OBJECT_BASE_CLASS_FULLNAME = f"{importlib.util.resolve_name('...', __package__)}.AsyncObject"


class AsyncObjectPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> Callable[[FunctionContext], Type] | None:
        if fullname == _ASYNC_OBJECT_BASE_CLASS_FULLNAME:
            return async_class_instanciation_callback

        node = self._get_type_info_if_AsyncObject_subclass(fullname)
        if node is None:
            return None
        return async_class_instanciation_callback

    def get_base_class_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None:
        node = self._get_type_info_if_AsyncObject_subclass(fullname)
        if node is None:
            return None
        return async_class_def_callback

    def _get_type_info_if_AsyncObject_subclass(self, fullname: str) -> TypeInfo | None:
        symbol_table_node: SymbolTableNode | None = self.lookup_fully_qualified(fullname)
        if symbol_table_node is None:
            return None
        node = symbol_table_node.node
        if not isinstance(node, TypeInfo):
            return None
        if not node.has_base(_ASYNC_OBJECT_BASE_CLASS_FULLNAME):
            return None
        return node


def async_class_instanciation_callback(ctx: FunctionContext) -> Type:
    return ctx.api.named_generic_type(
        "typing.Coroutine",
        [
            AnyType(TypeOfAny.implementation_artifact),
            AnyType(TypeOfAny.implementation_artifact),
            ctx.default_return_type,
        ],
    )


def async_class_def_callback(ctx: ClassDefContext) -> None:
    info = ctx.cls.info

    for ctor in ("__new__", "__init__"):
        node = info.names.get(ctor)
        if node is None or node.node is None:
            continue

        new_ctor_name: str | None = None
        if ctor in {"__init__"}:
            new_ctor_name = f"__async_{ctor[2:-2]}_mypy_placeholder"

        func_items: Sequence[SymbolNode]
        if isinstance(node.node, OverloadedFuncDef):
            func_items = node.node.items
        else:
            func_items = [node.node]

        for defn in func_items:
            if isinstance(defn, Decorator):
                defn = defn.func
            elif not isinstance(defn, FuncDef):
                continue
            if not defn.is_coroutine:
                ctx.api.fail(
                    f'"{ctor}" must be a coroutine function (using "async def")',
                    defn,
                    serious=True,
                    code=errorcodes.OVERRIDE,
                )
                continue
            if new_ctor_name is not None:
                __set_func_def_name(defn, new_ctor_name)

        if new_ctor_name is not None:
            info.names[new_ctor_name] = info.names[ctor]

    if info.get_method("__await__") is not None:
        ctx.api.fail('AsyncObject subclasses must not have "__await__" method', ctx.cls, code=errorcodes.OVERRIDE)


def __set_func_def_name(defn: FuncDef, name: str) -> None:
    if hasattr(defn, "_name"):
        old_name = defn.name
        defn._name = name
        if getattr(defn, "_fullname", None) and defn.fullname.endswith(old_name):
            prefix, dot, _ = defn.fullname.rpartition(".")
            if dot:
                defn._fullname = dot.join([prefix, name])
            else:
                defn._fullname = name

        print(defn.name, ",", defn.fullname)


def plugin(version: str) -> type[Plugin]:
    return AsyncObjectPlugin

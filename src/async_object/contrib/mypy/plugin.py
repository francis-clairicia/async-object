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

    for ctor in {"__init__"}:
        node = info.names.get(ctor)
        if node is None or node.node is None:
            continue

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
            __set_func_def_name(defn, new_ctor_name)

        info.names[new_ctor_name] = info.names[ctor]

    if dunder_await_node := info.names.get("__await__"):
        node_ctx = dunder_await_node.node if dunder_await_node.node else ctx.cls
        ctx.api.fail(
            'AsyncObject subclasses must not have "__await__" method',
            node_ctx,
            serious=True,
            code=errorcodes.OVERRIDE,
        )
    elif base_classes_with_dunder_await := [cls_info.defn.name for cls_info in info.mro[1:] if "__await__" in cls_info.names]:
        ctx.api.fail(
            f"These base classes define __await__: {', '.join(map(repr, base_classes_with_dunder_await))}",
            ctx.cls,
            serious=True,
            code=errorcodes.OVERRIDE,
        )

    non_async_base_class_info_list = list(
        filter(lambda cls_info: not cls_info.has_base(_ASYNC_OBJECT_BASE_CLASS_FULLNAME), info.mro[1:-1])
    )

    if non_async_base_classes_with_dunder_init := [
        cls_info.defn.name for cls_info in non_async_base_class_info_list if "__init__" in cls_info.names
    ]:
        ctx.api.fail(
            f"These non-async base classes define a custom __init__: {', '.join(map(repr, non_async_base_classes_with_dunder_init))}",
            ctx.cls,
            serious=True,
            code=errorcodes.OVERRIDE,
        )


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


def plugin(version: str) -> type[Plugin]:
    return AsyncObjectPlugin

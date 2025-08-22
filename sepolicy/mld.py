# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import itertools
from collections.abc import Hashable
from typing import (
    Dict,
    Generator,
    Generic,
    List,
    Tuple,
    TypeVar,
)

T = TypeVar('T')

def with_nones(t: Tuple[Hashable]):
    choices = ((x, None) for x in t)
    yield from itertools.product(*choices)

class MultiLevelDict(Generic[T]):
    def __init__(self):
        self.__data: Dict[int, Dict[Tuple[Hashable, ...], List[T]]] = {}

    def data(self):
        return self.__data

    def walk(self):
        for levels in self.__data.keys():
            t = tuple([None] * levels)
            yield from self.__data[levels][t]

    def add(self, keys: Tuple[Hashable], value: T):
        levels = len(keys)
        levels_data = self.__data.setdefault(levels, {})
        for t in with_nones(keys):
            levels_data.setdefault(t, []).append(value)

    def remove(self, keys: List[Hashable], value: T):
        levels = len(keys)
        assert levels in self.__data
        print('remove', value)
        for t in with_nones(keys):
            self.__data[levels][t].remove(value)

    def match(
        self,
        keys: Tuple[Hashable],
    ) -> Generator[T]:
        levels = len(keys)
        if levels not in self.__data:
            return

        levels_data = self.__data[levels]
        if keys not in levels_data:
            return

        yield from levels_data[keys]

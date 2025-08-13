# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from typing import (
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

T = TypeVar('T')


multi_level_type = Dict[str, Union['multi_level_type', List[T]]]


match_value_fn_type = Callable[[T], bool]
match_index_fn_type = Callable[[int, str], Tuple[bool, List[str]]]
match_success_fn_type = Callable[[T, List[str]], None]


class MultiLevelDictMatchData:
    def __init__(self):
        pass


class MultiLevelDictMatcher(Generic[T]):
    def __init__(
        self,
        match_value_fn: match_value_fn_type,
        match_index_fn: match_index_fn_type,
        match_success_fn: match_success_fn_type,
    ):
        self.match_value_fn = match_value_fn
        self.match_index_fn = match_index_fn
        self.match_success_fn = match_success_fn


class MultiLevelDict(Generic[T]):
    def __init__(self):
        self.__data: multi_level_type = {}
        self.__list: List[Optional[T]] = []
        self.__data_keys: Dict[T, List[str]] = {}
        self.__data_index: Dict[T, Optional[int]] = {}

    def index(self, value: T):
        return self.__data_index[value]

    def at(self, index: Optional[int]):
        assert index is not None

        if index >= len(self.__list):
            return None

        return self.__list[index]

    def _add_to_list(self, keys: List[str], value: T):
        self.__list.append(value)
        index = len(self.__list) - 1
        self.__data_index[value] = index
        self.__data_keys[value] = keys

    def _remove_from_list(self, value: T):
        index = self.index(value)
        self.__list[index] = None
        self.__data_index[value] = None
        self.__data_keys[value] = None

    def add(self, keys: List[str], value: T):
        self._add_to_list(keys, value)

        data = self.__data

        for i, index in enumerate(keys):
            if i != len(keys) - 1:
                data = data.setdefault(index, {})
                continue

            data = data.setdefault(index, [])

            if value not in data:
                data.append(value)

    def _remove(self, data: multi_level_type, keys: List[str], value: T):
        self._remove_from_list(keys, value)

        key = keys[0]

        if key not in data:
            return

        if isinstance(data[key], dict):
            self._remove(data[key], keys[1:], value)
        elif isinstance(data[key], list) and value in data[key]:
            data[key].remove(value)

        if not len(data[key]):
            data.pop(key)

    def remove(self, keys: List[str], value: T):
        return self._remove(self.__data, keys, value)

    def _walk_list(
        self,
        data: List[T],
        matcher: MultiLevelDictMatcher,
        match_data: MultiLevelDictMatchData,
    ):
        for value in data:
            if not matcher.match_value_fn(value):
                continue

            matcher.match_success_fn(value, match_data)

    def _walk(
        self,
        data: multi_level_type,
        matcher: MultiLevelDictMatcher,
        level: int,
        match_data: MultiLevelDictMatchData,
    ):
        for key in data.keys():
            new_match_data = matcher.match_index_fn(
                level,
                key,
                match_data,
            )
            if new_match_data is None:
                continue

            if isinstance(data[key], dict):
                self._walk(data[key], matcher, level + 1, new_match_data)
            else:
                self._walk_list(data[key], matcher, new_match_data)

    def walk(
        self,
        matcher: MultiLevelDictMatcher,
        match_data: MultiLevelDictMatchData,
    ):
        self._walk(self.__data, matcher, 0, match_data)

    def _match_value(
        self,
        value: T,
        matcher: MultiLevelDictMatcher,
        match_data: MultiLevelDictMatchData,
    ):
        value_keys = self.__data_keys[value]

        for level, key in enumerate(value_keys):
            match_data = matcher.match_index_fn(
                level,
                key,
                match_data,
            )

            if match_data is None:
                return

            if not matcher.match_value_fn(value):
                return

        matcher.match_success_fn(value, match_data)

    def match_next_value(
        self,
        value: T,
        matcher: MultiLevelDictMatcher,
        match_data: MultiLevelDictMatchData,
    ):
        index = self.index(value)
        next_index = index + 1
        next_value = self.at(next_index)
        if next_value is None:
            return None

        self._match_value(next_value, matcher, match_data)

    def __str__(self):
        return json.dumps(self.__data, indent=4, default=str)

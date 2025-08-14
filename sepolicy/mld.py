# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from collections.abc import Hashable
from typing import Callable, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar('T')


multi_level_type = Dict[Hashable, Union['multi_level_type', List[T]]]


class MultiLevelDictMatchData:
    def __init__(self):
        pass


match_value_fn_type = Callable[[T], bool]
match_success_fn_type = Callable[[T, List[Hashable]], None]
match_keys_fn_type = Callable[
    [Hashable, MultiLevelDictMatchData],
    Optional[List[MultiLevelDictMatchData]],
]


class MultiLevelDictMatcher(Generic[T]):
    def __init__(
        self,
        match_keys: List[Hashable | match_keys_fn_type],
        is_value_match_fn: match_value_fn_type,
        match_success_fn: match_success_fn_type,
    ):
        self.match_keys = match_keys
        self.is_value_match_fn = is_value_match_fn
        self.match_success_fn = match_success_fn


class MultiLevelDict(Generic[T]):
    def __init__(self):
        self.__data: multi_level_type = {}

    def add(self, keys: List[Hashable], value: T):
        # TODO: allow all kinds of hashable keys

        data = self.__data

        for i, key in enumerate(keys):
            if i != len(keys) - 1:
                data = data.setdefault(key, {})
                continue

            data = data.setdefault(key, [])

            if value not in data:
                data.append(value)

    def _remove(self, data: multi_level_type, keys: List[Hashable], value: T):
        key = keys[0]

        if key not in data:
            return

        if isinstance(data[key], dict):
            self._remove(data[key], keys[1:], value)
        elif isinstance(data[key], list) and value in data[key]:
            data[key].remove(value)

        if not len(data[key]):
            data.pop(key)

    def remove(self, keys: List[Hashable], value: T):
        return self._remove(self.__data, keys, value)

    def _match_list(
        self,
        data: List[T],
        matcher: MultiLevelDictMatcher,
        match_data: MultiLevelDictMatchData,
    ):
        for value in data:
            if not matcher.is_value_match_fn(value):
                continue

            matcher.match_success_fn(value, match_data)

    def _matching_keys(
        self,
        data: multi_level_type,
        matcher: MultiLevelDictMatcher,
        level: int,
        match_data: MultiLevelDictMatchData,
    ):
        match_level_key = matcher.match_keys[level]

        if not callable(match_level_key):
            if match_level_key in data.keys():
                yield (match_level_key, match_data)

            return

        for key in data.keys():
            new_match_datas = match_level_key(key, match_data)
            for new_match_data in new_match_datas:
                yield (key, new_match_data)

    def _match(
        self,
        data: multi_level_type,
        matcher: MultiLevelDictMatcher,
        level: int,
        match_data: MultiLevelDictMatchData,
    ):
        valid_keys_match_data = self._matching_keys(
            data,
            matcher,
            level,
            match_data,
        )

        for key, new_match_data in valid_keys_match_data:
            if isinstance(data[key], dict):
                self._match(data[key], matcher, level + 1, new_match_data)
            else:
                self._match_list(data[key], matcher, new_match_data)

    def match(
        self,
        matcher: MultiLevelDictMatcher,
        match_data: MultiLevelDictMatchData,
    ):
        self._match(self.__data, matcher, 0, match_data)

    def __str__(self):
        return json.dumps(self.__data, indent=4, default=str)

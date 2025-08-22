# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Dict, Optional, Self


class RuleMatchData:
    def __init__(self, data: Optional[Dict[int, str]] = None):
        if data is None:
            data = {}

        self.__data: Dict[int, str] = data

    def can_add(self, arg_index: int, arg_value: str):
        if arg_index not in self.__data:
            return True

        return self.__data[arg_index] == arg_value

    def add(self, arg_index: int, arg_value: str) -> Self:
        if arg_index in self.__data:
            assert self.__data[arg_index] == arg_value
            return self

        data = self.__data.copy()
        data[arg_index] = arg_value
        return RuleMatchData(data)

    def data(self):
        return self.__data

    def __hash__(self):
        return hash(frozenset(self.__data.items()))


def macro_rule_is_simple_match(part: str):
    # Match single-argument strings since they can have any type
    # of parameters
    return part[0] == '$' and part[1:].isdigit()


def macro_rule_extract_simple_match_arg_index(part: str):
    return int(part[1:])

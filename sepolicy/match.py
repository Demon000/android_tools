# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from collections.abc import Hashable
from functools import partial
from re import Pattern
from typing import Dict, Iterable, List, Optional, Self

from mld import (
    MultiLevelDict,
    MultiLevelDictMatchData,
    MultiLevelDictMatcher,
    match_keys_fn_type,
)
from rule import Rule, RuleType, macro_argument_regex


class RuleMatchData(MultiLevelDictMatchData):
    def __init__(self, data: Optional[Dict[int, str]] = None):
        if data is None:
            data = {}

        self.__data: Dict[int, str] = data

    def can_add(self, arg_index: int, arg_value: str):
        if arg_index not in self.__data:
            return True

        return self.__data[arg_index] == arg_value

    def add(self, arg_index: int, arg_value: str):
        self.__data[arg_index] = arg_value

    def data(self):
        return self.__data

    def duplicate(self) -> Self:
        return RuleMatchData(self.__data.copy())

    def __hash__(self):
        return hash(frozenset(self.__data.items()))


def macro_rule_identity(
    key: Hashable,
    match_data: MultiLevelDictMatchData,
):
    return [match_data]


def macro_rule_string_match_fn(
    regex: Pattern[str],
    arg_indices: List[int],
    key: Hashable,
    match_data: MultiLevelDictMatchData,
):
    assert isinstance(match_data, RuleMatchData), match_data

    if not isinstance(key, str):
        return []

    regex_match = regex.match(key)
    if regex_match is None:
        return []

    if not regex_match:
        return []

    regex_match_groups = regex_match.groups()

    new_match_data = match_data.duplicate()
    for arg_group_index, arg_index in enumerate(arg_indices):
        arg_value = regex_match_groups[arg_group_index]
        assert arg_value

        if not new_match_data.can_add(arg_index, arg_value):
            return []

        new_match_data.add(arg_index, arg_value)

    return [new_match_data]


def macro_rule_iter_match_fn(
    match_keys: List[match_keys_fn_type],
    key: Hashable,
    match_data: MultiLevelDictMatchData,
):
    for i, match_key in enumerate(match_keys):
        if not callable(match_key):
            if match_key == key[i]:
                continue

            return None

        match_data = match_key(key[i], match_data)
        if match_data is None:
            return None

    return match_data


def macro_rule_frozenset_match_fn(
    match_keys: List[match_keys_fn_type],
    key: Hashable,
    match_data: MultiLevelDictMatchData,
):
    if not isinstance(key, frozenset):
        return None

    new_match_datas = []
    # sets have no order, match any with any
    for part in key:
        for match_key in match_keys:
            match_datas = 
            if not callable(match_key):
                if match_key == part:
                    new_match_datas.append(match_data)
                continue

            match_datas = match_key(part, match_data)
            new_match_datas.append(match_datas)
            if match_data is None:
                continue



def macro_rule_get_string_match_key(part: str):
    if '$' not in part:
        return part

    # Find all used argument indices in this macro part
    arg_indices = [int(i) for i in macro_argument_regex.findall(part)]
    for arg_index in arg_indices:
        assert arg_index <= 9

    # Escape the characters in this part of the macro rule
    regex = re.escape(part)

    # Replace escaped $arg with a capture group
    regex = re.sub(r'\\\$(\d+)', r'(.+)', regex)
    regex = re.compile(regex)

    return partial(macro_rule_string_match_fn, regex, arg_indices)


def macro_rule_get_iter_match_keys(i: Iterable):
    match_keys = []
    for part in i:
        match_key = macro_rule_get_part_match_key(part)
        match_keys.append(match_key)
    return match_keys


def macro_rule_get_iter_match_key(i: Iterable):
    match_keys = macro_rule_get_iter_match_keys(i)
    return partial(macro_rule_iter_match_fn, match_keys)


def macro_rule_get_frozenset_match_key(f: frozenset):
    match_keys = macro_rule_get_iter_match_keys(f)
    return partial(macro_rule_frozenset_match_fn, match_keys)


def macro_rule_get_part_match_key(part: str | list | tuple):
    if isinstance(part, str):
        match_key = macro_rule_get_string_match_key(part)
    elif isinstance(part, list | tuple):
        match_key = macro_rule_get_iter_match_key(part)
    elif isinstance(part, frozenset):
        match_key = macro_rule_get_frozenset_match_key(part)
    else:
        assert False, part

    return match_key


def macro_rule_get_match_keys(rule: Rule):
    match_keys: List[Hashable | match_keys_fn_type] = [rule.rule_type]
    for part in rule.parts:
        match_key = macro_rule_get_part_match_key(part)
        match_keys.append(match_key)
    return match_keys


def match_success_fn(
    matched_rule: Rule,
    new_match_data: MultiLevelDictMatchData,
    new_match_datas_rules: Dict[RuleMatchData, List[Rule]],
    matched_rules: List[Rule],
):
    assert isinstance(new_match_data, RuleMatchData), new_match_data
    new_match_datas_rules.setdefault(new_match_data, matched_rules[:]).append(
        matched_rule
    )


def is_value_match_fn(match_rule: Rule, rule: Rule):
    return rule.varargs == match_rule.varargs


def macro_rule_match(
    mld: MultiLevelDict,
    rule: Rule,
    match_data: RuleMatchData,
    matched_rules: List[Rule],
    new_match_datas_rules: Dict[RuleMatchData, List[Rule]],
):
    match_keys = macro_rule_get_match_keys(rule)

    is_value_match = partial(
        is_value_match_fn,
        rule=rule,
    )
    match_success = partial(
        match_success_fn,
        matched_rules=matched_rules,
        new_match_datas_rules=new_match_datas_rules,
    )

    matcher: MultiLevelDictMatcher[Rule] = MultiLevelDictMatcher(
        match_keys,
        is_value_match,
        match_success,
    )

    mld.match(matcher, match_data)


def macro_rule_replace_string_match_data(
    s: str,
    match_data: RuleMatchData,
):
    if '$' not in s:
        return s

    for arg_index, arg_value in match_data.data().items():
        s = s.replace(f'${arg_index}', arg_value)

    return s


def macro_rule_replace_iter_match_data(
    i: Iterable,
    match_data: RuleMatchData,
):
    new_parts = []
    for part in i:
        part = macro_rule_replace_part_match_data(part, match_data)
        new_parts.append(part)
    return new_parts


def macro_rule_replace_part_match_data(
    part: str | list | tuple | frozenset,
    match_data: RuleMatchData,
):
    if isinstance(part, str):
        part = macro_rule_replace_string_match_data(part, match_data)
    elif isinstance(part, list):
        part = macro_rule_replace_iter_match_data(part, match_data)
    elif isinstance(part, tuple):
        part = macro_rule_replace_iter_match_data(part, match_data)
        part = tuple(part)
    elif isinstance(part, frozenset):
        part = macro_rule_replace_iter_match_data(part, match_data)
        part = frozenset(part)
    else:
        assert False, part

    return part


def macro_rule_replace_match_data(rule: Rule, match_data: RuleMatchData):
    new_parts = macro_rule_replace_iter_match_data(rule.parts, match_data)

    return Rule(rule.rule_type, new_parts, rule.varargs)


def match_macro_rules(
    mld: MultiLevelDict,
    macro_name: str,
    macro_rules: List[Rule],
    matched_macro_rules: List[Rule],
):
    print(f'Processing macro: {macro_name}')

    match_datas_rules: Dict[RuleMatchData, List[Rule]] = {
        RuleMatchData(): [],
    }

    for macro_rule in macro_rules:
        print(f'Processing rule: {macro_rule}')
        new_match_datas_rules: Dict[RuleMatchData, List[Rule]] = {}
        for match_data, matched_rules in match_datas_rules.items():
            filled_rule = macro_rule_replace_match_data(macro_rule, match_data)
            # print(f'Filled macro rule: {filled_rule}', match_data.data())

            # Slim down the dictionary keys of match_datas while increasing the
            # number of rules stored in each list
            macro_rule_match(
                mld,
                filled_rule,
                match_data,
                matched_rules,
                new_match_datas_rules,
            )

        if not new_match_datas_rules:
            print('No matches for rule', macro_rule)
            print()
            return

        match_datas_rules = new_match_datas_rules

    for match_data, match_data_rules in match_datas_rules.items():
        # print(macro_name)
        # print(match_data.data())
        # for rule in match_data_rules:
        #     print(rule)
        # print()

        for match_data_rule in match_data_rules:
            try:
                mld.remove(match_data_rule.all_parts, match_data_rule)
            except ValueError as e:
                # typeattribute rules are split from typeattributeset rules,
                # which means we cannot figure out how many times they are
                # defined
                # This particularly happens for the pdx_service_socket_types
                # macro
                # Do not error out if the rule that couldn't be removed is
                # a typeattribute
                if match_data_rule.rule_type != RuleType.TYPEATTRIBUTE:
                    raise e

        # Extract match_data values sorted based on their arg index
        raw_match_data = match_data.data()
        args = [raw_match_data[k] for k in sorted(raw_match_data.keys())]
        macro_rule = Rule(macro_name, [], args)
        matched_macro_rules.append(macro_rule)

    print(f'Matched {len(match_datas_rules)} macros')

    print()

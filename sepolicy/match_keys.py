# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from collections.abc import Hashable
from functools import partial
from itertools import permutations
from re import Pattern
from typing import Callable, Iterable, List, Optional

from match_data import (
    RuleMatchData,
    macro_rule_extract_simple_match_arg_index,
    macro_rule_is_simple_match,
)
from rule import Rule, macro_argument_regex

match_keys_fn_type = Callable[
    [Hashable, RuleMatchData],
    Optional[List[RuleMatchData]],
]

def macro_rule_arg_match_fn(
    arg_index: int,
    key: Hashable,
    match_data: RuleMatchData,
):
    arg_value = key
    if not match_data.can_add(arg_index, arg_value):
        return []

    new_match_data = match_data.add(arg_index, arg_value)
    return [new_match_data]


def macro_rule_string_match_fn(
    regex: Pattern[str],
    arg_indices: List[int],
    key: Hashable,
    match_data: RuleMatchData,
):
    if not isinstance(key, str):
        return []

    regex_match = regex.match(key)
    if regex_match is None:
        return []

    if not regex_match:
        return []

    regex_match_groups = regex_match.groups()

    for arg_group_index, arg_index in enumerate(arg_indices):
        arg_value = regex_match_groups[arg_group_index]
        assert arg_value

        if not match_data.can_add(arg_index, arg_value):
            return []

    new_match_data = match_data
    for arg_group_index, arg_index in enumerate(arg_indices):
        arg_value = regex_match_groups[arg_group_index]
        new_match_data = new_match_data.add(arg_index, arg_value)

    return [new_match_data]


def macro_rule_iter_match_fn(
    match_keys: List[match_keys_fn_type],
    key: Hashable,
    match_data: RuleMatchData,
):
    if len(key) != len(match_keys):
        return []

    match_datas = [match_data]
    for i, match_key in enumerate(match_keys):
        new_match_datas = []
        for match_data in match_datas:
            if not callable(match_key):
                if match_key == key[i]:
                    new_match_datas.append(match_data)

                continue

            current_match_datas = match_key(key[i], match_data)
            new_match_datas.extend(current_match_datas)
        match_datas = new_match_datas

    return match_datas


def macro_rule_frozenset_match_fn(
    match_keys: List[match_keys_fn_type],
    key: Hashable,
    match_data: RuleMatchData,
):
    if not isinstance(key, frozenset):
        return []

    if len(key) != len(match_keys):
        return []

    # sets have no order, match all permutations
    all_match_keys = permutations(match_keys)
    match_datas = []
    for permuted_match_keys in all_match_keys:
        indexable_key = tuple(key)
        current_match_datas = macro_rule_iter_match_fn(
            permuted_match_keys,
            indexable_key,
            match_data,
        )
        match_datas.extend(current_match_datas)

    return match_datas


def macro_rule_get_string_match_key(part: str):
    # Match single-argument strings since they can have any type
    # of parameters
    if macro_rule_is_simple_match(part):
        arg_index = macro_rule_extract_simple_match_arg_index(part)
        return partial(macro_rule_arg_match_fn, arg_index)

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

    is_callable = False
    for match_key in match_keys:
        if callable(match_key):
            is_callable = True
            break

    if not is_callable:
        return match_keys

    return partial(macro_rule_iter_match_fn, match_keys)


def macro_rule_get_frozenset_match_key(f: frozenset):
    match_keys = macro_rule_get_iter_match_keys(f)

    is_callable = False
    for match_key in match_keys:
        if callable(match_key):
            is_callable = True
            break

    if not is_callable:
        return match_keys

    return partial(macro_rule_frozenset_match_fn, match_keys)


def macro_rule_get_part_match_key(part: str | tuple | frozenset):
    if isinstance(part, str):
        match_key = macro_rule_get_string_match_key(part)
    elif isinstance(part, tuple):
        match_key = macro_rule_get_iter_match_key(part)
        if not callable(match_key):
            match_key = tuple(match_key)
    elif isinstance(part, frozenset):
        match_key = macro_rule_get_frozenset_match_key(part)
        if not callable(match_key):
            match_key = frozenset(match_key)
    else:
        assert False, part

    return match_key


def macro_rule_get_match_keys(rule: Rule):
    match_keys: List[Optional[Hashable]] = [rule.rule_type]
    match_fns: List[Optional[match_keys_fn_type]] = [None]

    for part in rule.parts:
        match_key = macro_rule_get_part_match_key(part)
        if callable(match_key):
            match_keys.append(None)
            match_fns.append(match_key)
        else:
            match_keys.append(match_key)
            match_fns.append(None)

    return tuple(match_keys), match_fns

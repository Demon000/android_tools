# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from functools import partial
from typing import Iterable

from match_data import (
    RuleMatchData,
    macro_rule_extract_simple_match_arg_index,
    macro_rule_is_simple_match,
)
from rule import Rule


def macro_rule_replace_string_match_data(
    match_data: RuleMatchData,
    s: str,
):
    data = match_data.data()

    if macro_rule_is_simple_match(s):
        arg_index = macro_rule_extract_simple_match_arg_index(s)
        if arg_index not in data:
            return s

        return data[arg_index]

    if '$' not in s:
        return s

    for arg_index, arg_value in data.items():
        s = s.replace(f'${arg_index}', arg_value)

    return s


def macro_rule_replace_iter_match_data(
    match_data: RuleMatchData,
    i: Iterable,
):
    fn = partial(macro_rule_replace_part_match_data, match_data)
    return list(map(fn, i))


def macro_rule_replace_part_match_data(
    match_data: RuleMatchData,
    part: str | list | tuple | frozenset,
):
    if isinstance(part, str):
        part = macro_rule_replace_string_match_data(match_data, part)
    elif isinstance(part, list):
        part = macro_rule_replace_iter_match_data(match_data, part)
    elif isinstance(part, tuple):
        part = macro_rule_replace_iter_match_data(match_data, part)
        part = tuple(part)
    elif isinstance(part, frozenset):
        part = macro_rule_replace_iter_match_data(match_data, part)
        part = frozenset(part)
    else:
        assert False, part

    return part


def macro_rule_replace_match_data(match_data: RuleMatchData, rule: Rule):
    new_parts = macro_rule_replace_iter_match_data(match_data, rule.parts)

    return Rule(rule.rule_type, new_parts, rule.varargs)

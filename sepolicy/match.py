# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from re import Pattern
from typing import Dict, List, Optional, Self, Union

from mld import MultiLevelDict, MultiLevelDictMatchData, MultiLevelDictMatcher
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


def macro_rule_args_matching_data(rule: Rule):
    regexes: List[Union[str, Pattern[str]]] = [rule.rule_type.value]
    arg_indices: List[Optional[List[int]]] = [None]

    for part in rule.parts:
        if '$' not in part:
            # Keep a list of string-based matches to avoid running regex
            regexes.append(part)
            arg_indices.append(None)
            continue

        # Find all used argument indices in this macro part
        part_arg_indices = [int(i) for i in macro_argument_regex.findall(part)]
        for part_arg_index in part_arg_indices:
            assert part_arg_index <= 9

        # assert len(set(macro_part_arg_indices)) == 1, macro_rule

        # Escape the characters in this part of the macro rule
        part_regex = re.escape(part)

        # Replace escaped $arg with a capture group
        part_regex = re.sub(r'\\\$(\d+)', r'(.+)', part_regex)
        part_regex = re.compile(part_regex)

        regexes.append(part_regex)
        arg_indices.append(part_arg_indices)

    return regexes, arg_indices


def macro_rule_matcher(
    mld: MultiLevelDict,
    rule: Rule,
    match_data: RuleMatchData,
    matched_rules: List[Rule],
    new_match_datas: Dict[RuleMatchData, List[Rule]],
):
    regexes, arg_indices = macro_rule_args_matching_data(rule)
    varargs_set = set(rule.varargs)

    def match_success_fn(
        matched_rule: Rule,
        new_match_data: MultiLevelDictMatchData,
    ):
        assert isinstance(new_match_data, RuleMatchData), new_match_data
        print('Matched', matched_rule, new_match_data.data())
        new_match_datas.setdefault(new_match_data, matched_rules[:]).append(
            matched_rule
        )

    def match_value_fn(match_rule: Rule):
        assert (rule.varargs == match_rule.varargs) == (
            varargs_set == set(match_rule.varargs)
        )
        return varargs_set == set(match_rule.varargs)

    def match_index_fn(
        index_position: int,
        index: str,
        match_data: MultiLevelDictMatchData,
    ):
        assert isinstance(match_data, RuleMatchData), match_data
        regex = regexes[index_position]

        # If this part of the rule contains no args, only check if the
        # index matches and return the same match_data
        if isinstance(regex, str):
            if regex == index:
                return match_data

            return None

        regex_match = regex.match(index)
        if regex_match is None:
            return None

        if not regex_match:
            return None

        regex_match_groups = regex_match.groups()

        new_match_data = match_data.duplicate()
        for arg_group_index, arg_index in enumerate(
            arg_indices[index_position]
        ):
            arg_value = regex_match_groups[arg_group_index]
            assert arg_value

            if not new_match_data.can_add(arg_index, arg_value):
                return None

            new_match_data.add(arg_index, arg_value)

        return new_match_data

    matcher: MultiLevelDictMatcher[Rule] = MultiLevelDictMatcher(
        match_value_fn,
        match_index_fn,
        match_success_fn,
    )

    # All rule types except typeattribute should follow the previously
    # matched rule
    last_rule = None
    if (
        len(matched_rules) >= 1
        and matched_rules[-1].rule_type != RuleType.TYPEATTRIBUTE
    ):
        last_rule = matched_rules[-1]

    if last_rule is None:
        mld.walk(matcher, match_data)
    else:
        mld.match_next_value(last_rule, matcher, match_data)


def macro_rule_replace_match_data(rule: Rule, match_data: RuleMatchData):
    new_parts = []
    for part in rule.parts:
        if '$' not in part:
            new_parts.append(part)
            continue

        new_part = part
        for arg_index, arg_value in match_data.data().items():
            new_part = new_part.replace(f'${arg_index}', arg_value)

        new_parts.append(new_part)

    return Rule(rule.rule_type, new_parts, rule.varargs)


def match_macro_rules(
    mld: MultiLevelDict,
    macro_name: str,
    macro_rules: List[Rule],
):
    print(f'Matching macro: {macro_name}')

    match_datas: Dict[RuleMatchData, List[Rule]] = {
        RuleMatchData(): [],
    }

    for macro_rule in macro_rules:
        print(f'Matching macro rule: {macro_rule}')
        new_match_datas: Dict[RuleMatchData, List[Rule]] = {}
        for match_data, matched_rules in match_datas.items():
            filled_rule = macro_rule_replace_match_data(macro_rule, match_data)
            print(f'Filled macro rule: {filled_rule}')
            # This call should slim down the dictionary keys of match_datas while
            # increasing the number of rules stored in each list
            macro_rule_matcher(
                mld,
                filled_rule,
                match_data,
                matched_rules,
                new_match_datas,
            )
        match_datas = new_match_datas

    for match_data, matched_rules in match_datas.items():
        print(match_data.data())
        for rule in matched_rules:
            print(rule)
        print()

    exit()

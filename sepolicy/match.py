# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from functools import partial
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
    indices: List[Optional[str]] = [rule.rule_type]
    regexes: List[Optional[Pattern[str]]] = [None]
    arg_indices: List[Optional[List[int]]] = [None]

    for part in rule.parts:
        if '$' not in part:
            # Keep a list of string-based matches to avoid running regex
            indices.append(part)
            regexes.append(None)
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

        indices.append(None)
        regexes.append(part_regex)
        arg_indices.append(part_arg_indices)

    return regexes, indices, arg_indices


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


def is_index_match_fn(
    index_position: int,
    index: str,
    match_data: MultiLevelDictMatchData,
    regexes: List[Union[str, Pattern[str]]],
    arg_indices: List[Optional[List[int]]],
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
    for arg_group_index, arg_index in enumerate(arg_indices[index_position]):
        arg_value = regex_match_groups[arg_group_index]
        assert arg_value

        if not new_match_data.can_add(arg_index, arg_value):
            return None

        new_match_data.add(arg_index, arg_value)

    return new_match_data


def macro_rule_match(
    mld: MultiLevelDict,
    rule: Rule,
    match_data: RuleMatchData,
    matched_rules: List[Rule],
    new_match_datas_rules: Dict[RuleMatchData, List[Rule]],
):
    regexes, match_indices, arg_indices = macro_rule_args_matching_data(rule)

    is_index_match = partial(
        is_index_match_fn,
        regexes=regexes,
        arg_indices=arg_indices,
    )
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
        match_indices,
        is_value_match,
        is_index_match,
        match_success,
    )

    mld.match(matcher, match_data)


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

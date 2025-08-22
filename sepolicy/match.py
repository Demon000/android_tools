# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Dict, List

from match_data import RuleMatchData
from match_keys import macro_rule_get_match_keys, match_keys_fn_type
from match_replace import macro_rule_replace_match_data
from mld import MultiLevelDict
from rule import Rule, RuleType
from utils import Color, color_print


def macro_rule_match_one(
    match_fns: List[match_keys_fn_type],
    match_data: RuleMatchData,
    matched_rules: List[Rule],
    new_match_datas_rules_map: Dict[RuleMatchData, List[Rule]],
    matched_rule: Rule,
):
    # TODO: match a single rule for each rule in the macro
    # for each match data, but remove all occurances in the end

    print('matched_rule', matched_rule)
    print('match_data', match_data.data())

    match_datas = [match_data]
    for i, match_fn in enumerate(match_fns):
        if match_fn is None:
            continue

        print('i', i, match_fn)

        # TODO: need matching for rule types?
        assert i != 0
        key = matched_rule.parts[i - 1]
        print('key', key)

        new_match_datas = []
        for match_data in match_datas:
            current_match_datas = match_fn(key, match_data)
            new_match_datas.extend(current_match_datas)

        for match_data in new_match_datas:
            print('new_match_data', match_data.data())
        print()

        match_datas = new_match_datas

    for match_data in match_datas:
        new_match_datas_rules_map.setdefault(
            match_data, matched_rules[:]
        ).append(matched_rule)


def macro_rule_match(
    mld: MultiLevelDict[Rule],
    rule: Rule,
    match_data: RuleMatchData,
    matched_rules: List[Rule],
    new_match_datas_rules_map: Dict[RuleMatchData, List[Rule]],
):
    print('macro_rule_match', rule)
    match_keys, match_fns = macro_rule_get_match_keys(rule)
    print('match_keys', match_keys)

    for matched_rule in mld.match(match_keys):
        if matched_rule.varargs != rule.varargs:
            return

        print('rule', rule)

        macro_rule_match_one(
            rule,
            match_fns,
            match_data,
            matched_rules,
            new_match_datas_rules_map,
            matched_rule,
        )


def match_macro_rules(
    mld: MultiLevelDict[Rule],
    macro_name: str,
    macro_rules: List[Rule],
    matched_macro_rules: List[Rule],
):
    # TODO: figure out unix_socket_connect and unix_socket_send
    # not being formed into set_prop
    print(f'Processing macro: {macro_name}')

    match_datas_rules: Dict[RuleMatchData, List[Rule]] = {
        RuleMatchData(): [],
    }

    for macro_rule in macro_rules:
        print(f'Processing rule: {macro_rule}')

        new_match_datas_rules_map: Dict[RuleMatchData, List[Rule]] = {}
        for match_data, matched_rules in match_datas_rules.items():
            filled_rule = macro_rule_replace_match_data(match_data, macro_rule)

            macro_rule_match(
                mld,
                filled_rule,
                match_data,
                matched_rules,
                new_match_datas_rules_map,
            )

        if not new_match_datas_rules_map:
            color_print('No matches for rule', macro_rule, color=Color.YELLOW)
            print()
            return

        match_datas_rules = new_match_datas_rules_map

        # for match_data, match_data_rules in match_datas_rules.items():
        #     print('Matched', match_data.data())
        #     for rule in match_data_rules:
        #         print(rule)
        #     print

    for match_data, match_data_rules in match_datas_rules.items():
        print('match_data', match_data.data())
        for match_data_rule in match_data_rules:
            print(match_data_rule)
        print()

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
        macro_rule = Rule(macro_name, args, [], is_macro=True)
        matched_macro_rules.append(macro_rule)

    color_print(
        f'Matched {len(match_datas_rules)} {macro_name} calls',
        color=Color.GREEN,
    )
    print()

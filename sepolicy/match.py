# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Dict, List, Optional, Set

from match_extract import (
    args_type,
    merge_arg_values,
    rule_extract_part,
    rule_extract_part_iter,
)
from match_replace import rule_replace_part_iter
from mld import MultiLevelDict
from rule import Rule, rule_part_or_varargs
from utils import Color, color_print


class RuleMatch:
    def __init__(
        self,
        macro_name: str,
        rules: Set[Rule] = set(),
        arg_values: args_type = {},
    ):
        self.macro_name = macro_name
        self.rules = rules
        self.arg_values = arg_values
        self.hash_values = tuple(
            [
                self.macro_name,
                frozenset(self.arg_values.items()),
            ]
        )
        self.hash = hash(self.hash_values)

        args = tuple(arg_values[k] for k in sorted(arg_values.keys()))
        self.macro = Rule(macro_name, args, tuple(), is_macro=True)

    def filled_args(self):
        return self.arg_values.keys()

    def add_arg_values(self, arg_values: args_type) -> Optional[RuleMatch]:
        new_arg_values = merge_arg_values(self.arg_values, arg_values)
        if new_arg_values is None:
            return None

        return RuleMatch(self.macro_name, self.rules.copy(), new_arg_values)

    def add_rule(self, rule: Rule):
        self.rules.add(rule)

    def __hash__(self):
        return self.hash

    def __eq__(self, other: object):
        assert isinstance(other, RuleMatch)

        return self.hash_values == other.hash_values

    def __str__(self):
        return str(self.macro)


def rule_match_keys(rule: Rule, is_match_keys_full: bool):
    match_keys: List[Optional[rule_part_or_varargs]] = [rule.rule_type]

    for part in rule.parts:
        # A fully filled rule doesn't need to have its parts tested
        # to check if they need to be filled
        if is_match_keys_full:
            match_keys.append(part)
            continue

        # Match part to itself to see if it has any args
        part_args_values = rule_extract_part(part, part)

        if part_args_values:
            match_keys.append(None)
        else:
            match_keys.append(part)

    match_keys.append(rule.varargs)

    return match_keys


def rule_fill(rule: Rule, arg_values: args_type):
    new_parts = rule_replace_part_iter(rule.parts, arg_values)
    if new_parts is None:
        return None

    return Rule(rule.rule_type, tuple(new_parts), rule.varargs)


def match_macro_rule(
    mld: MultiLevelDict[Rule],
    macro_rule: Rule,
    macro_rule_index: int,
    rule_matches: Set[RuleMatch],
):
    print(f'Processing rule: {macro_rule}')

    macro_rule_args = rule_extract_part_iter(
        macro_rule.parts,
        macro_rule.parts,
    )
    assert macro_rule_args is not None

    # Check if this rule requires only already completed args
    rule_match = next(iter(rule_matches))
    is_match_keys_full = macro_rule_args.keys() <= rule_match.filled_args()

    new_rule_matches: Set[RuleMatch] = set()
    for rule_match in rule_matches:
        # print(f'Initial args: {rule_match.arg_values}')

        # TODO: make rule args extraction build a path that can be used for
        # filling no matter the args
        filled_rule = rule_fill(macro_rule, rule_match.arg_values)
        if filled_rule is None:
            continue

        # print(f'Filled rule: {filled_rule}')

        match_keys = rule_match_keys(filled_rule, is_match_keys_full)
        # print(f'Match keys: {match_keys}')

        for matched_rule in mld.match(match_keys):
            # print(f'Matched rule: {matched_rule}')

            # If the rule is fully filled don't expand the matches
            if is_match_keys_full:
                rule_match.add_rule(matched_rule)
                new_rule_matches.add(rule_match)
                # print()
                break

            new_args_values = rule_extract_part_iter(
                filled_rule.parts,
                matched_rule.parts,
            )
            if new_args_values is None:
                continue

            new_rule_match = rule_match.add_arg_values(new_args_values)
            if new_rule_match is None:
                continue

            new_rule_match.add_rule(matched_rule)
            new_rule_matches.add(new_rule_match)

    return new_rule_matches


def match_macro_rules(
    mld: MultiLevelDict[Rule],
    macro_name: str,
    macro_rules: List[Rule],
    all_rule_matches: Set[RuleMatch],
):
    print(f'Processing macro: {macro_name}')

    rule_matches: Set[RuleMatch] = set([RuleMatch(macro_name)])
    for macro_rule_index, macro_rule in enumerate(macro_rules):
        new_rule_matches = match_macro_rule(
            mld,
            macro_rule,
            macro_rule_index,
            rule_matches,
        )
        print(f'Found {len(new_rule_matches)} candidates')
        if not len(new_rule_matches):
            print()
            return

        rule_matches = new_rule_matches

    all_rule_matches.update(rule_matches)

    print(f'Found {len(rule_matches)} macro calls')
    print()


def discard_superset_rule_matches(
    mld: MultiLevelDict[Rule],
    all_rule_matches: Set[RuleMatch],
    macro_rules: List[Rule],
):
    color_print(
        f'All rule matches: {len(all_rule_matches)}',
        color=Color.GREEN,
    )

    rule_matches_map: Dict[Rule, Set[RuleMatch]] = {}
    for rule_match in all_rule_matches:
        for rule in rule_match.rules:
            if rule not in rule_matches_map:
                rule_matches_map[rule] = set()
            rule_matches_map[rule].add(rule_match)

    discarded_rule_matches: Set[RuleMatch] = set()

    for rule_match in all_rule_matches:
        candidate_supersets: Optional[Set[RuleMatch]] = None

        for rule in rule_match.rules:
            rule_matches = rule_matches_map[rule]

            if candidate_supersets is None:
                candidate_supersets = rule_matches
            else:
                candidate_supersets = candidate_supersets & rule_matches

        assert candidate_supersets is not None

        candidate_supersets.remove(rule_match)

        for candidate in candidate_supersets:
            if rule_match.rules < candidate.rules or (
                rule_match.rules == candidate.rules
                and len(rule_match.arg_values) > len(candidate.arg_values)
            ):
                # print(f'Macro {rule_match} subset of {candidate}')
                discarded_rule_matches.add(rule_match)
                break

    color_print(
        f'Discarded subset rule matches: {len(discarded_rule_matches)}',
        color=Color.GREEN,
    )

    for rule_match in discarded_rule_matches:
        all_rule_matches.remove(rule_match)

    color_print(
        f'Rule matches: {len(all_rule_matches)}',
        color=Color.GREEN,
    )

    double_removed_rules: Set[Rule] = set()
    for rule_match in all_rule_matches:
        macro_rules.append(rule_match.macro)
        for rule in rule_match.rules:
            try:
                mld.remove(rule.hash_values, rule)
            except KeyError:
                if rule in double_removed_rules:
                    continue

                color_print(
                    f'Rule already removed: {rule}',
                    color=Color.YELLOW,
                )
                double_removed_rules.add(rule)

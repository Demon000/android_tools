#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import List, Set, Tuple

from cil import decompile_cil
from classmap import SELINUX_INCLUDE_PATH, Classmap
from config import default_variables
from macro import (
    categorize_macros,
    decompile_macros,
    expand_macro_bodies,
    macro_conditionals,
    macro_name,
    read_macros,
    resolve_macro_paths,
    split_macros_text_name_body,
)
from match import RuleMatch, discard_superset_rule_matches, match_macro_rules
from match_extract import rule_extract_part_iter
from mld import MultiLevelDict
from rule import Rule


def print_macro_file_paths(macro_file_paths: List[str]):
    for macro_path in macro_file_paths:
        print(f'Loading macros from {macro_path}')


def print_variable_ifelse(macros: List[str]):
    handled_variable_macro_ifelse = [
        'domain_trans',
    ]

    # Find conditional variables used in the input text
    # Conditional variables can be specified, but we need to know if the
    # macro arguments are used in them
    for macro in macros:
        name = macro_name(macro)
        if name in handled_variable_macro_ifelse:
            continue

        conditional_variables = macro_conditionals(macro)
        for conditional_variable in conditional_variables:
            if conditional_variable.startswith('$'):
                print(
                    f'Macro {name} contains variable ifelse: {conditional_variable}'
                )


def rule_arity(rule: Rule):
    macro_rule_args = rule_extract_part_iter(
        rule.parts,
        rule.parts,
    )
    assert macro_rule_args is not None
    return len(macro_rule_args)


def macro_sort_key(macro: Tuple[str, List[Rule]]):
    rules = macro[1]
    arities = list(map(rule_arity, rules))
    max_arity = max(arities, default=0)

    return (-len(macro[1]), max_arity)


def sort_macros(macros: List[Tuple[str, List[Rule]]]):
    # Inside the macro, prefer rules with higher arity to help
    # the arg matching algorithm
    # TODO: sort so that rules using higher args are preferred
    for macro in macros:
        rules = macro[1]
        rules.sort(key=rule_arity, reverse=True)

    # Sort by number of rules and arity, prefer macros with more rules and
    # lower arity
    # This is important for define_prop() wrappers that have the same number
    # of rules as define_prop() but lower arity
    # TODO: not needed for matching all macros and then rulling them out
    # macros.sort(key=macro_sort_key)


if __name__ == '__main__':
    parser = ArgumentParser(
        prog='decompile_cil.py',
        description='Decompile CIL files',
    )
    parser.add_argument('cil', nargs='+')
    parser.add_argument(
        '-m',
        '--macros',
        action='append',
        default=[],
        help='Path to directories or files containing macros',
    )
    parser.add_argument(
        '-k',
        '--kernel',
        action='store',
        required=True,
        help='Path to kernel (external/selinux/python/sepolgen/src/share/perm_map)',
    )
    parser.add_argument(
        '-v',
        '--var',
        action='append',
        default=[],
        help='Variable used when expanding macros',
    )
    parser.add_argument(
        '-o',
        '--output',
        action='store',
        help='Output directory for the decompiled selinux',
    )

    args = parser.parse_args()
    assert args.macros

    variables = {**default_variables}

    for kv in args.var:
        k, v = kv.split('=')
        variables[k] = v

    rules = decompile_cil(args.cil)

    mld: MultiLevelDict[Rule] = MultiLevelDict()
    for rule in rules:
        # Add partial matches to this rule
        # Start partial matching after the first key
        mld.add(rule.hash_values, rule)

    macro_file_paths = resolve_macro_paths(args.macros)

    print_macro_file_paths(macro_file_paths)

    input_text, macros_text = read_macros(macro_file_paths)

    print_variable_ifelse(macros_text)

    expanded_macros_text = expand_macro_bodies(
        input_text,
        macros_text,
        variables,
    )
    macros_name_body = split_macros_text_name_body(expanded_macros_text)

    expanded_macros, class_sets, perms, ioctls, ioctl_defines = (
        categorize_macros(macros_name_body)
    )

    # classmap is needed to sort classes and perms to match the compiled
    # output
    selinux_include_path = Path(args.kernel, SELINUX_INCLUDE_PATH).resolve()
    classmap = Classmap(str(selinux_include_path))

    macros_name_rules = decompile_macros(classmap, expanded_macros)

    sort_macros(macros_name_rules)

    all_rule_matches: Set[RuleMatch] = set()
    for name, rules in macros_name_rules:
        match_macro_rules(
            mld,
            name,
            rules,
            all_rule_matches,
        )

    macro_rules: List[Rule] = []
    discard_superset_rule_matches(mld, all_rule_matches, macro_rules)

    print('Macro rules')
    for rule in macro_rules:
        print(rule)

    print('Leftover rules')
    for rule in mld.walk():
        print(rule)

    # TODO: merge back typeattribute rules

    # TODO: use class_sets macros
    # TODO: use perms macros
    # TODO: use ioctls macros
    # TODO: use ioctl defines macros

    # TODO: output property_contexts, file_contexts, hwservice_contexts, genfs_contexts
    # TODO: output rules and macros to file
    # TODO: output app signing certificates

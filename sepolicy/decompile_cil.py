#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import List

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
    sort_macros,
    split_macros_text_name_body,
)
from match import match_macro_rules
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
        mld.add(rule.all_parts, rule)

    # import pprint
    # pprint.pp(mld.data())
    # exit()

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
    selinux_include_path = Path(args.kernel, SELINUX_INCLUDE_PATH)
    classmap = Classmap(selinux_include_path)

    macros_name_rules = decompile_macros(classmap, expanded_macros)

    sort_macros(macros_name_rules)

    matched_macro_rules: List[Rule] = []
    for name, rules in macros_name_rules:
        match_macro_rules(mld, name, rules, matched_macro_rules)

    print('Matched rules')
    for rule in matched_macro_rules:
        print(rule)

    print('Leftover rules')
    for rule in mld.walk():
        print(rule)

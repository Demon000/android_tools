#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import shutil
from argparse import ArgumentParser
from functools import partial
from itertools import chain
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cil_rule import CilRule
from classmap import SELINUX_INCLUDE_PATH, Classmap
from conditional_type import ConditionalType
from config import default_variables
from macro import (
    categorize_macros,
    decompile_ioctl_defines,
    decompile_ioctls,
    decompile_macros,
    decompile_perms,
    expand_macro_bodies,
    macro_conditionals,
    macro_name,
    read_macros,
    resolve_macro_paths,
    split_macros_text_name_body,
)
from match import (
    RuleMatch,
    match_macro_rules,
    merge_class_sets,
    merge_ioctl_rules,
    merge_typeattribute_rules,
    replace_ioctls,
    replace_macro_rules,
    replace_perms,
)
from match_extract import rule_extract_part_iter
from mld import MultiLevelDict
from output import (
    group_rules,
    output_contexts,
    output_genfs_contexts,
    output_grouped_rules,
)
from rule import RULE_DYNAMIC_PARTS_INDEX, Rule
from utils import Color, color_print


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
    for macro in macros:
        rules = macro[1]
        rules.sort(key=rule_arity, reverse=True)

    # Sort by number of rules and arity, prefer macros with more rules and
    # lower arity
    # This is important for define_prop() wrappers that have the same number
    # of rules as define_prop() but lower arity
    # TODO: not needed for matching all macros and then rulling them out
    # macros.sort(key=macro_sort_key)


def decompile_cil(cil_paths: List[str]):
    cil_datas = [Path(p).read_text() for p in cil_paths]
    cils_data = '\n'.join(cil_datas)

    cil_lines = cils_data.splitlines()

    conditional_types_map: Dict[str, ConditionalType] = {}
    missing_generated_types: Set[str] = set()
    genfs_rules: List[Rule] = []

    # Convert lines to rules
    fn = partial(
        CilRule.from_line,
        conditional_types_map=conditional_types_map,
        missing_generated_types=missing_generated_types,
        genfs_rules=genfs_rules,
    )
    rules = list(chain.from_iterable(map(fn, cil_lines)))

    return rules, genfs_rules


def get_cil_paths(selinux_dir: str):
    selinux_path = Path(selinux_dir)
    return [str(p) for p in selinux_path.glob('*.cil')]


if __name__ == '__main__':
    parser = ArgumentParser(
        prog='decompile_cil.py',
        description='Decompile CIL files',
    )
    parser.add_argument('cil', nargs='*')
    parser.add_argument(
        '-s',
        '--selinux',
        action='store',
        help='Path to selinux directory',
    )
    # TODO: determine sepolicy version automatically and find macros dir
    # based on android root
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
        required=True,
        help='Output directory for the decompiled selinux',
    )
    # TODO: add seapp certificates base path

    args = parser.parse_args()
    assert args.macros

    variables = {**default_variables}

    for kv in args.var:
        k, v = kv.split('=')
        variables[k] = v

    output_dir: str = args.output
    kernel_dir: str = args.kernel
    selinux_dir: Optional[str] = args.selinux
    cil_paths: List[str] = args.cil

    if not cil_paths:
        assert selinux_dir is not None
        cil_paths = get_cil_paths(selinux_dir)

    rules, genfs_rules = decompile_cil(cil_paths)

    mld: MultiLevelDict[Rule] = MultiLevelDict()
    for rule in rules:
        # Add partial matches to this rule
        # Start partial matching after the first key
        mld.add(rule.hash_values, rule, RULE_DYNAMIC_PARTS_INDEX)

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
    decompiled_perms = decompile_perms(perms)
    decompiled_class_sets = decompile_perms(class_sets)
    decompiled_ioctls = decompile_ioctls(ioctls)
    decompiled_ioctl_defines = decompile_ioctl_defines(ioctl_defines)

    # classmap is needed to sort classes and perms to match the compiled
    # output
    selinux_include_path = Path(kernel_dir, SELINUX_INCLUDE_PATH).resolve()
    classmap = Classmap(str(selinux_include_path))

    macros_name_rules = decompile_macros(classmap, expanded_macros)

    sort_macros(macros_name_rules)

    color_print(f'Total rules: {len(mld)}', color=Color.GREEN)

    all_rule_matches: Set[RuleMatch] = set()
    for name, rules in macros_name_rules:
        match_macro_rules(
            mld,
            name,
            rules,
            all_rule_matches,
        )

    replace_macro_rules(mld, all_rule_matches)
    merge_typeattribute_rules(mld)
    merge_ioctl_rules(mld)

    replace_perms(mld, classmap, decompiled_perms)
    replace_ioctls(mld, decompiled_ioctls, decompiled_ioctl_defines)
    merge_class_sets(mld, decompiled_class_sets)

    # We can also merge target domains, but rules get long quickly
    # merge_target_domains(mld)

    color_print(f'Leftover rules: {len(mld)}', color=Color.GREEN)

    grouped_rules = group_rules(mld)

    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)

    output_contexts(selinux_dir, output_dir)
    output_genfs_contexts(genfs_rules, output_dir)
    output_grouped_rules(grouped_rules, output_dir)

    # TODO: output app signing certificates

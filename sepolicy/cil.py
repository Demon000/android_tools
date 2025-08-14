# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from functools import partial
from itertools import chain
from pathlib import Path
from typing import Dict, List, Set, Union

from cil_rule import CilRule
from mld import MultiLevelDict
from rule import Rule, is_type_generated, parts_list


def replace_generated_part(
    m: Dict[str, str],
    missing_generated_types: Set[str],
    part: Union[parts_list, str],
):
    # base_typeattr_ is not found in the nested lists
    if not isinstance(part, str):
        return part

    if not is_type_generated(part):
        return part

    if part not in m:
        if part not in missing_generated_types:
            print(f'Generated type {part} not found')
            missing_generated_types.add(part)

        return part

    return m[part]


def replace_generated_typeattributeset(
    m: Dict[str, str],
    missing_generated_types: Set[str],
    rule: Rule,
):
    for i, part in enumerate(rule.parts):
        rule.parts[i] = replace_generated_part(m, missing_generated_types, part)


def decompile_cil(cil_paths: List[str]):
    cil_datas = [Path(p).read_text() for p in cil_paths]
    cils_data = '\n'.join(cil_datas)

    cil_lines = cils_data.splitlines()

    conditional_types_map: Dict[str, str] = {}
    genfs_rules: List[Rule] = []

    # Convert lines to rules
    fn = partial(
        CilRule.from_line,
        conditional_types_map=conditional_types_map,
        genfs_rules=genfs_rules,
    )
    rules = list(chain.from_iterable(map(fn, cil_lines)))

    # Replace conditional types with readable format
    # These types are not specified in order of appeatance
    missing_generated_types: Set[str] = set()
    for rule in rules:
        replace_generated_typeattributeset(
            conditional_types_map,
            missing_generated_types,
            rule,
        )

    mld: MultiLevelDict[Rule] = MultiLevelDict()
    for rule in rules:
        mld.add(rule.all_parts, rule)

    return mld

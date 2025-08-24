# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from functools import partial
from itertools import chain
from pathlib import Path
from typing import Dict, List, Set

from cil_rule import CilRule
from conditional_type import ConditionalType
from rule import Rule


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

    return rules

# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from functools import cache
from pathlib import Path
from typing import Dict, List, Optional, Set

from mld import MultiLevelDict
from rule import Rule, RuleType

VENDOR_PREFIX = 'vendor_'
PROPERTY_CONTEXTS_NAME = 'property_contexts'
FILE_CONTEXTS_NAME = 'file_contexts'
HWSERVICE_CONTEXTS_NAME = 'hwservice_contexts'
SERVICE_CONTEXTS_NAME = 'service_contexts'
SEAPP_CONTEXTS_NAME = 'seapp_contexts'
GENFS_CONTEXTS_NAME = 'genfs_contexts'
MAC_PERMISSIONS_NAME = 'mac_permissions.xml'
KEYS_NAME = 'keys.conf'


def copy_contexts(input_path: str, output_path: str):
    # TODO: align parts against eachother?

    lines: List[str] = []
    with open(input_path, 'r') as file:
        for line in file.readlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith('#'):
                continue

            line = re.sub(r'\s+', ' ', line)
            lines.append(line)

    lines.sort()

    with open(output_path, 'w') as file:
        for line in lines:
            file.write(line)
            file.write('\n')


def output_contexts(selinux_dir: Optional[str], output_dir: str):
    if selinux_dir is None:
        return

    for name in [
        PROPERTY_CONTEXTS_NAME,
        FILE_CONTEXTS_NAME,
        HWSERVICE_CONTEXTS_NAME,
        SERVICE_CONTEXTS_NAME,
        SEAPP_CONTEXTS_NAME,
    ]:
        input_path = Path(selinux_dir, name)
        if not input_path.exists():
            input_path = Path(selinux_dir, f'{VENDOR_PREFIX}{name}')

        if not input_path.exists():
            continue

        output_path = Path(output_dir, name)
        copy_contexts(str(input_path), str(output_path))


def output_genfs_contexts(genfs_rules: List[Rule], output_dir: str):
    output_path = Path(output_dir, GENFS_CONTEXTS_NAME)
    with open(output_path, 'w') as o:
        for rule in genfs_rules:
            o.write(str(rule))
            o.write('\n')


@cache
def extract_domain_type(domain: str):
    domain = re.sub(r'^vendor_', '', domain)
    domain = re.sub(r'_exec$', '', domain)
    domain = re.sub(r'_client$', '', domain)
    domain = re.sub(r'_server$', '', domain)
    domain = re.sub(r'_default$', '', domain)
    domain = re.sub(r'_hwservice$', '', domain)
    domain = re.sub(r'_qti$', '', domain)
    return domain


DEVICE_TYPE_RULES_NAME = 'device.te'
FILE_TYPE_RULES_NAME = 'file.te'
PROPERTY_RULES_NAME = 'property.te'
LEFTOVER_RULES_NAME = 'leftover.te'
ATTRIBUTE_RULES_NAME = 'attribute'


def group_rules(mld: MultiLevelDict[Rule]):
    grouped_rules: Dict[str, Set[Rule]] = {}

    for rule in mld.walk():
        # device types
        if rule.rule_type == RuleType.TYPE.value and 'dev_type' in rule.varargs:
            name = DEVICE_TYPE_RULES_NAME
        # file types
        elif rule.rule_type == RuleType.TYPE.value and (
            'file_type' in rule.varargs or 'fs_type' in rule.varargs
        ):
            name = FILE_TYPE_RULES_NAME
        # attributes
        elif (
            rule.rule_type == RuleType.ATTRIBUTE.value
            or rule.rule_type == RuleType.EXPANDATTRIBUTE.value
        ):
            name = ATTRIBUTE_RULES_NAME
        # property
        elif isinstance(rule.parts[0], str) and rule.parts[0].endswith('_prop'):
            name = PROPERTY_RULES_NAME
        elif isinstance(rule.parts[0], str):
            t = extract_domain_type(rule.parts[0])
            name = f'{t}.te'
        else:
            name = LEFTOVER_RULES_NAME

        if name not in grouped_rules:
            grouped_rules[name] = set()

        grouped_rules[name].add(rule)

    return grouped_rules


def rules_sort_key(rule: Rule):
    compare_values = [str(h) for h in rule.hash_values]
    return (rule.is_macro, compare_values)


def output_grouped_rules(grouped_rules: Dict[str, Set[Rule]], output_dir: str):
    for name, rules in grouped_rules.items():
        sorted_rules = sorted(rules, key=rules_sort_key)

        output_path = Path(output_dir, name)
        with open(output_path, 'w') as o:
            last_type = None
            for rule in sorted_rules:
                if last_type is not None and rule.rule_type != last_type:
                    o.write('\n')
                last_type = rule.rule_type
                o.write(str(rule))
                o.write('\n')

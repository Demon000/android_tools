# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from enum import StrEnum
from typing import List, Set

from type import parts_list

macro_argument_regex = re.compile(r'\$(\d+)')


def flatten_parts(parts: parts_list):
    if isinstance(parts, str):
        yield parts
        return

    for part in parts:
        if isinstance(part, list):
            yield from flatten_parts(part)
        else:
            yield part


def unpack_line(
    rule: str,
    open_char: str,
    close_char: str,
    separators: str,
    open_by_default=False,
    ignored_chars='',
) -> parts_list:
    stack = []
    current = []
    token = ''

    def add_token():
        nonlocal token

        if token:
            current.append(token)
            token = ''

    if open_by_default:
        rule = f'{open_char}{rule}{close_char}'

    for c in rule:
        if c in ignored_chars:
            continue

        if c == open_char:
            add_token()
            stack.append(current)
            current = []
        elif c == close_char:
            add_token()
            last = stack.pop()
            last.append(current)
            current = last
        elif c in separators:
            add_token()
        else:
            token += c

    return current[0] if current else []


class RuleType(StrEnum):
    ALLOW = 'allow'
    ALLOWXPERM = 'allowxperm'
    ATTRIBUTE = 'attribute'
    AUDITALLOW = 'auditallow'
    DONTAUDIT = 'dontaudit'
    DONTAUDITXPERM = 'dontauditxperm'
    EXPANDATTRIBUTE = 'expandattribute'
    GENFSCON = 'genfscon'
    NEVERALLOW = 'neverallow'
    NEVERALLOWXPERM = 'neverallowxperm'
    TYPE = 'type'
    TYPE_TRANSITION = 'type_transition'
    TYPEATTRIBUTE = 'typeattribute'


OUT_OF_ORDER_RULE_TYPES = set(
    [
        RuleType.EXPANDATTRIBUTE.value,
        RuleType.TYPE.value,
        RuleType.TYPEATTRIBUTE.value,
        RuleType.TYPE_TRANSITION.value,
        RuleType.ATTRIBUTE.value,
    ]
)


class Rule:
    def __init__(
        self,
        rule_type: str,
        parts: List[str],
        varargs: List[str],
    ):
        self.rule_type = rule_type
        self.parts = parts
        self.varargs = varargs

    @property
    def all_parts(self):
        return [self.rule_type] + self.parts

    def __str__(self):
        return f'{self.rule_type} {self.parts} {self.varargs}'

    def __hash__(self):
        return hash(tuple([tuple(self.all_parts), frozenset(self.varargs)]))

    def arity(self):
        arg_indices: Set[int] = set()

        for part in self.parts:
            if '$' not in part:
                continue

            part_arg_indices = [
                int(i) for i in macro_argument_regex.findall(part)
            ]
            arg_indices.update(part_arg_indices)

        return len(arg_indices)

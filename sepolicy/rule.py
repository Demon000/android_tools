# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from enum import Enum
from typing import List, Optional, Tuple, Union

from conditional_type import IConditionalType

macro_argument_regex = re.compile(r'\$(\d+)')

raw_part = Union[str, List['raw_part']]
raw_parts_list = List[raw_part]
rule_part = Union[str, IConditionalType]
rule_part_or_varargs = Union[rule_part, Tuple[str, ...]]



VERSION_SUFFIXES = set(
    [
        '_202404',
        '_34_0',
        '_33_0',
        '_32_0',
        '_31_0',
        '_30_0',
        '_29_0',
    ]
)


# TODO: optimize
def remove_type_suffix(t: str):
    for suffix in VERSION_SUFFIXES:
        if t.endswith(suffix):
            return t[: -len(suffix)]

    return t


def is_type_generated(part: rule_part):
    if not isinstance(part, str):
        return False

    return part.startswith('base_typeattr_')


def unpack_line(
    rule: str,
    open_char: str,
    close_char: str,
    separators: str,
    open_by_default: bool = False,
    ignored_chars: str = '',
) -> raw_parts_list:
    # TODO: test ~{ a b } formatting for source rules

    stack: List[raw_parts_list] = []
    current: raw_parts_list = []
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

    assert isinstance(current[0], list)

    return current[0] if current else []


def remove_ioctl_zeros(ioctls: List[str]):
    return list(map(lambda i: hex(int(i, base=16)), ioctls))


class RuleType(str, Enum):
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


def join_varargs(varargs: Tuple[str, ...]):
    s = ' '.join(varargs)

    if len(varargs) > 1:
        s = '{ ' + s + ' }'

    return s


def format_rule(rule: Rule):
    match rule.rule_type:
        case (
            RuleType.ALLOW
            | RuleType.NEVERALLOW
            | RuleType.AUDITALLOW
            | RuleType.DONTAUDIT
        ):
            return '{} {} {}:{} {};'.format(
                rule.rule_type,
                rule.parts[0],
                rule.parts[1],
                rule.parts[2],
                join_varargs(rule.varargs),
            )
        case (
            RuleType.ALLOWXPERM
            | RuleType.NEVERALLOWXPERM
            | RuleType.DONTAUDITXPERM
        ):
            return '{} {} {}:{} ioctl {};'.format(
                rule.rule_type,
                rule.parts[0],
                rule.parts[1],
                rule.parts[2],
                join_varargs(rule.varargs),
            )
        case RuleType.TYPE:
            varargs = sorted(rule.varargs)
            varargs_str = ', '.join(varargs)
            return '{} {}, {};'.format(
                rule.rule_type, rule.parts[0], varargs_str
            )
        case RuleType.TYPE_TRANSITION:
            # TODO: can the varargs depend on args?

            assert len(rule.varargs) in [0, 1]

            if len(rule.varargs) == 1:
                name = f'{list(rule.varargs)[0]} '
            else:
                name = ''

            return '{} {} {}:{} {}{};'.format(
                rule.rule_type,
                rule.parts[0],
                rule.parts[1],
                rule.parts[2],
                name,
                rule.parts[-1],
            )
        case RuleType.GENFSCON:
            return 'genfscon {} {} u:object_r:{}:s0;'.format(
                rule.parts[0],
                rule.parts[1],
                rule.parts[2],
            )
        case (
            RuleType.ATTRIBUTE
            | RuleType.TYPEATTRIBUTE
            | RuleType.EXPANDATTRIBUTE
        ):
            parts_str = ' '.join(map(str, rule.parts))
            return f'{rule.rule_type} {parts_str};'
        case _:
            assert rule.is_macro
            parts_str = ', '.join(map(str, rule.parts))
            return f'{rule.rule_type}({parts_str})'


class Rule:
    def __init__(
        self,
        rule_type: str,
        parts: Tuple[rule_part, ...],
        varargs: Tuple[str, ...],
        is_macro: bool = False,
    ):
        self.rule_type = rule_type
        self.parts = parts
        self.varargs = tuple(varargs)
        self.is_macro = is_macro
        self.hash_values: Tuple[rule_part_or_varargs, ...] = tuple(
            [self.rule_type] + list(self.parts) + [self.varargs]
        )

        # Postpone hash calculation so that ConditionalTypes are fully
        # gathered and ConditionalTypeRedirect can find them
        self.__hash: Optional[int] = None

    def __str__(self):
        return format_rule(self)

    def __eq__(self, other: object):
        assert isinstance(other, Rule)

        return self.hash_values == other.hash_values

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash(self.hash_values)

        return self.__hash

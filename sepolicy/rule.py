# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from collections.abc import Hashable
from enum import StrEnum
from typing import List, Set, Union

macro_argument_regex = re.compile(r'\$(\d+)')

parts_list = List[Union['parts_list', str]]

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


def is_type_generated(t: str):
    return t.startswith('base_typeattr_')


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
    # TODO: test ~{ a b } formatting for source rules

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


def remove_ioctl_zeros(ioctls: List[str]):
    return list(map(lambda i: hex(int(i, base=16)), ioctls))


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


def join_varargs(varargs: List[str]):
    s = ' '.join(varargs)

    if len(varargs) > 1:
        s = '{ ' + s + ' }'

    return s


def format_conditional_type(part: str | List[Union[str, frozenset[str]]]):
    if isinstance(part, str):
        return part

    if part == tuple(['all']):
        return '*'

    s = ''
    if part[0] == 'and' and len(part) in [2, 4]:
        s += '{'
        for a in part[1]:
            s += f' {a}'
        if len(part) == 4 and part[2] == 'not':
            for n in part[3]:
                s += f' -{n}'
        s += ' }'
    elif part[0] == 'not':
        s += '~'

        if len(part[1]):
            s += '{'
        for n in part[1]:
            s += f' {n}'
        if len(part[1]):
            s += ' }'
    else:
        assert False, part

    return s


def format_rule(rule: Rule):
    match rule.rule_type:
        case (
            RuleType.ALLOW
            | RuleType.NEVERALLOW
            | RuleType.AUDITALLOW
            | RuleType.DONTAUDIT
        ):
            src = format_conditional_type(rule.parts[0])
            dst = format_conditional_type(rule.parts[1])
            return '{} {} {}:{} {};'.format(
                rule.rule_type,
                src,
                dst,
                rule.parts[2],
                join_varargs(rule.varargs),
            )
        case (
            RuleType.ALLOWXPERM
            | RuleType.NEVERALLOWXPERM
            | RuleType.DONTAUDITXPERM
        ):
            src = format_conditional_type(rule.parts[0])
            dst = format_conditional_type(rule.parts[1])
            return '{} {} {}:{} {} {};'.format(
                rule.rule_type,
                src,
                dst,
                rule.parts[2],
                rule.parts[3],
                join_varargs(rule.varargs),
            )
        case RuleType.TYPE:
            varargs = sorted(rule.varargs)
            varargs_str = ', '.join(varargs)
            return '{} {}, {};'.format(
                rule.rule_type, rule.parts[0], varargs_str
            )
        case RuleType.TYPE_TRANSITION:
            assert len(rule.varargs) in [0, 1]

            if len(rule.varargs) == 1:

                name = f'{list(rule.varargs)[0]} '
            else:
                name = ''

            src = format_conditional_type(rule.parts[0])
            dst = format_conditional_type(rule.parts[1])
            return '{} {} {}:{} {}{};'.format(
                rule.rule_type,
                src,
                dst,
                rule.parts[2],
                name,
                rule.parts[-1],
            )
        case RuleType.GENFSCON:
            return '{} {} {} {}:{}:{}:{};'.format(
                rule.rule_type,
                *rule.parts,
            )
        case (
            RuleType.ATTRIBUTE
            | RuleType.TYPEATTRIBUTE
            | RuleType.EXPANDATTRIBUTE
        ):
            all_parts_str = ' '.join(rule.all_parts)
            return f'{all_parts_str};'
        case _:
            assert rule.is_macro
            parts_str = ', '.join(rule.parts)
            return f'{rule.rule_type}({parts_str})'


class Rule:
    def __init__(
        self,
        rule_type: str,
        parts: List[Hashable],
        varargs: List[str],
        is_macro=False,
    ):
        self.rule_type = rule_type
        self.parts = tuple(parts)
        self.varargs = frozenset(varargs)
        self.is_macro = is_macro

    @property
    def all_parts(self):
        return tuple([self.rule_type] + list(self.parts))

    def __str__(self):
        return format_rule(self)

    def __hash__(self):
        return hash(tuple(self.all_parts, self.varargs))

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

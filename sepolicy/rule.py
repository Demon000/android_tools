# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from enum import StrEnum
from typing import List, Set, Union

macro_argument_regex = re.compile(r'\$(\d+)')

parts_list = List[Union['parts_list', str]]


def flatten_typeattr_varargs(varargs: parts_list):
    if isinstance(varargs[0], list):
        varargs = varargs[0]

    if len(varargs) == 3 and isinstance(varargs[2][0], list):
        varargs[2] = varargs[2][0]

    return varargs


def is_conditional_typeattr(varargs: parts_list):
    return varargs[0] in ['and', 'not', 'all']


def expand_base_typeattr(varargs: parts_list):
    # TODO
    # Find out why
    # neverallow { domain -$1 -crash_dump userdebug_or_eng(`-llkd') -runas_app -simpleperf } $1:process ptrace;
    #
    # behaves like
    # neverallow { domain -crash_dump userdebug_or_eng(`-llkd') -runas_app -simpleperf -$1 } $1:process ptrace;
    #
    # Example:
    # (typeattributeset base_typeattr_748_31_0 ((and (domain) ((not (crash_dump_31_0 runas_app_31_0 simpleperf_31_0 soterservice_app_31_0))))))
    s = ''
    if varargs[0] == 'and' and len(varargs) == 3 and varargs[2][0] == 'not':
        s += '{'
        for a in varargs[1]:
            s += f' {a}'
        for n in varargs[2][1]:
            s += f' -{n}'
        s += ' }'
    elif (
        varargs[0] == 'and'
        and len(varargs) == 3
        and len(varargs[1]) == 1
        and len(varargs[2]) == 1
    ):
        # typeattribute { system_property_type && vendor_property_type } system_and_vendor_property_type;
        s += '{ '
        s += varargs[1][0]
        s += ' && '
        s += varargs[2][0]
        s += ' }'
    elif varargs[0] == 'not':
        s += '~'

        if len(varargs[1]) == 1:
            s += varargs[1][0]
        else:
            s += '{'
            for n in varargs[1]:
                s += f' {n}'
            s += ' }'
    elif varargs[0] == 'all':
        s = '*'
    else:
        assert False, varargs

    return s


VERSION_SUFFIXES = set(
    [
        '_29_0',
        '_30_0',
        '_31_0',
        '_32_0',
        '_33_0',
        '_34_0',
        '_202404',
    ]
)


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
    # TODO: allow ~{ a b } formatting for source rules

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

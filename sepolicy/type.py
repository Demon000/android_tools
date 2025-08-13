# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import List, Union

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
    s = ''
    if varargs[0] == 'and' and len(varargs) == 3 and varargs[2][0] == 'not':
        s += '{'
        for a in varargs[1]:
            s += f' {a}'
        for n in varargs[2][1]:
            s += f' -{n}'
        s += ' }'
    elif varargs[0] == 'and' and len(varargs) == 3 and len(varargs[1]) == 1 and len(varargs[2]) == 1:
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


class Type:
    @staticmethod
    def is_generated(t: str):
        return t.startswith('base_typeattr_')

    @staticmethod
    def sanitize(t: str):
        for suffix in VERSION_SUFFIXES:
            if t.endswith(suffix):
                return t[: -len(suffix)]

        return t

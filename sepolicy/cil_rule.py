# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from enum import StrEnum
from typing import Dict, List, Set

from rule import (
    Rule,
    RuleType,
    is_type_generated,
    parts_list,
    unpack_line,
)


def is_conditional_typeattr(varargs: parts_list):
    if isinstance(varargs[0], list):
        vararg = varargs[0][0]
    else:
        vararg = varargs[0]

    return vararg in ['and', 'not', 'all']


def is_handwritten_typeattributeset(varargs: parts_list):
    return isinstance(varargs[0], list)


def structure_typeattr_varargs(varargs: parts_list):
    # ((and (...) ((not (...))))) -> (and (...) ((not (...))))
    # ((not (...))) -> (not (...))

    if len(varargs) == 1 and isinstance(varargs[0], list):
        varargs = varargs[0]
        assert varargs[0] in ['and', 'not', 'all'], varargs

    # (and (...) ((not (...)))) -> (and (...) (not (...)))
    if (
        len(varargs) == 3
        and isinstance(varargs[2], list)
        and len(varargs[2]) == 1
        and varargs[2][0][0] == 'not'
    ):
        varargs[2] = varargs[2][0]

    # (and (...) (not (...))) -> (and (...) not (...))
    if (
        len(varargs) == 3
        and varargs[0] == 'and'
        and isinstance(varargs[2], list)
        and varargs[2][0] == 'not'
    ):
        assert isinstance(varargs[2], list)
        varargs.append(varargs[2][1])
        varargs[2] = varargs[2][0]

    for i, vararg in enumerate(varargs):
        if vararg in ['and', 'not']:
            for t in varargs[i + 1]:
                if not isinstance(t, str):
                    print('Ignored conditional type', varargs)
                    return None

            varargs[i + 1] = frozenset(varargs[i + 1])

    return tuple(varargs)


def is_valid_cil_line(line: str):
    line = line.strip()

    if not line:
        return False

    if line.startswith('#'):
        return False

    if line.startswith(';'):
        return False

    return True


def is_allow_process_sigchld(parts: parts_list):
    return (
        parts[0] == RuleType.ALLOW
        and len(parts) == 4
        and parts[3] == ['process', ['sigchld']]
    )


def unpack_ioctls(parts: parts_list):
    for part in parts:
        if isinstance(part, str):
            yield part
        elif isinstance(part, list):
            if isinstance(part[0], list):
                part = part[0]

            assert part[0] == 'range'
            start_ioctl = int(part[1], base=16)
            end_ioctl = int(part[2], base=16)
            for n in range(start_ioctl, end_ioctl + 1):
                yield hex(n)


class CilRuleType(StrEnum):
    ALLOWX = 'allowx'
    NEVERALLOWX = 'neverallowx'
    DONTAUDITX = 'dontauditx'
    EXPANDTYPEATTRIBUTE = 'expandtypeattribute'
    TYPEATTRIBUTESET = 'typeattributeset'
    TYPETRANSITION = 'typetransition'


unknown_rule_types: Set[str] = set(
    [
        'category',
        'categoryorder',
        'class',
        'classcommon',
        'classorder',
        'handleunknown',
        'mls',
        'mlsconstrain',
        'policycap',
        'role',
        'roleattribute',
        'roletype',
        'sensitivity',
        'sensitivitycategory',
        'sensitivityorder',
        'sid',
        'sidcontext',
        'sidorder',
        'fsuse',
        'common',
        'type',
        'typealias',
        'typealiasactual',
        'user',
        'userlevel',
        'userrange',
        'userrole',
    ]
)


class CilRule(Rule):
    @classmethod
    def from_line(
        cls,
        line: str,
        conditional_types_map: Dict[str, str],
        genfs_rules: List[Rule],
    ) -> List[Rule]:
        # Skip comments and empty lines
        if not is_valid_cil_line(line):
            return []

        parts = unpack_line(line, '(', ')', ' ')
        if not parts:
            return []

        # Remove rules that don't have a meaningful source mapping
        if parts[0] in unknown_rule_types:
            return []

        # Remove allow $3 $1:process sigchld as it is part of an ifelse
        # statement based on one of the parameters and it is not possible
        # to generate the checks for it as part of macro expansion
        if is_allow_process_sigchld(parts):
            return []

        if parts[0] == RuleType.TYPEATTRIBUTE:
            # Remove generated typeattribute as it does not map to a source rule
            if is_type_generated(parts[1]):
                return []

            # Rename typeattribute to attribute to match source
            # typeattribute rules in source expand to typeattributeset,
            # while attribute rules expand to typeattribute
            parts[0] = RuleType.ATTRIBUTE.value
        elif parts[0] == CilRuleType.TYPEATTRIBUTESET:
            # TODO: remove version of types
            # theorethically the version exists, but if expandtypeattribute
            # is set to true then a single-value typeattributeset will
            # cause expansion
            # Example:
            # (expandtypeattribute (netutils_wrapper_31_0) true)
            # (typeattributeset netutils_wrapper_31_0 (netutils_wrapper))

            if is_conditional_typeattr(parts[2]):
                varargs = structure_typeattr_varargs(parts[2])
                if varargs is None:
                    return []

                conditional_types_map.setdefault(parts[1], varargs)
            else:
                # Expand typeattributeset into multiple typeattribute rules
                rules = []
                for t in parts[2]:
                    assert isinstance(t, str)

                    rule = Rule(RuleType.TYPEATTRIBUTE.value, [t, parts[1]], [])
                    rules.append(rule)

                return rules

            return []
        elif parts[0] == CilRuleType.TYPETRANSITION:
            parts[0] = RuleType.TYPE_TRANSITION.value
        elif parts[0] == CilRuleType.EXPANDTYPEATTRIBUTE:
            parts[0] = RuleType.EXPANDATTRIBUTE.value
        elif parts[0] == CilRuleType.ALLOWX:
            parts[0] = RuleType.ALLOWXPERM.value
        elif parts[0] == CilRuleType.NEVERALLOWX:
            parts[0] = RuleType.NEVERALLOWXPERM.value
        elif parts[0] == CilRuleType.DONTAUDITX:
            parts[0] = RuleType.DONTAUDITXPERM.value

        rule_type = RuleType[parts[0].upper()].value
        parts = parts[1:]

        match rule_type:
            case (
                RuleType.ALLOW
                | RuleType.NEVERALLOW
                | RuleType.AUDITALLOW
                | RuleType.DONTAUDIT
            ):
                assert len(parts) == 3, line
                assert len(parts[2]) == 2, line
                varargs = parts[2][1]
                new_parts = parts[:2] + [parts[2][0]]
            case (
                RuleType.ALLOWXPERM
                | RuleType.NEVERALLOWXPERM
                | RuleType.DONTAUDITXPERM
            ):
                assert len(parts) == 3, line
                assert len(parts[2]) == 3, line
                varargs = list(unpack_ioctls(parts[2][2]))
                new_parts = parts[:2] + parts[2][:2]
            case RuleType.ATTRIBUTE:
                assert len(parts) == 1, line
                varargs = []
                new_parts = parts
            case RuleType.GENFSCON:
                assert len(parts) == 3, line
                assert len(parts[2]) == 4, line
                assert len(parts[2][3]) == 2, line
                assert len(parts[2][3][0]) == 1, line
                assert len(parts[2][3][1]) == 1, line
                varargs = []
                new_parts = parts[:2] + [parts[2][2]]
            case RuleType.TYPE_TRANSITION:
                assert len(parts) in [4, 5], line
                varargs = parts[3:-1]
                new_parts = parts[:3] + [parts[-1]]
            case RuleType.EXPANDATTRIBUTE:
                assert len(parts[0]) == 1
                varargs = []
                new_parts = [parts[0][0]] + parts[1:]
            case _:
                assert False, line

        rule = cls(rule_type, new_parts, varargs)

        if rule_type == RuleType.GENFSCON:
            genfs_rules.append(rule)
            return []

        return [rule]

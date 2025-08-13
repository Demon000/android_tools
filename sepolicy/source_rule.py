# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import List

from classmap import Classmap
from rule import Rule, RuleType, flatten_parts, unpack_line
from type import parts_list


def is_allow_process_sigchld(parts: parts_list):
    return (
        parts[0] == RuleType.ALLOW
        and len(parts) == 5
        and parts[3:] == ['process', 'sigchld']
    )


class SourceRule(Rule):
    @classmethod
    def from_line(cls, line: str, classmap: Classmap) -> List[Rule]:
        parts = unpack_line(
            line,
            '{',
            '}',
            ' :,',
            open_by_default=True,
            ignored_chars=';',
        )
        if not parts:
            return []

        if not isinstance(parts[0], str):
            raise ValueError(f'Invalid line: {line}')

        try:
            rule_type = RuleType[parts[0].upper()].value
        except KeyError:
            raise ValueError(f'Invalid line: {line}')

        # Remove allow $3 $1:process sigchld as it is part of an ifelse
        # statement based on one of the parameters and it is not possible
        # to generate the checks for it as part of macro expansion
        if is_allow_process_sigchld(parts):
            return []

        parts = parts[1:]
        rules = []

        match rule_type:
            case (
                RuleType.ALLOW
                | RuleType.NEVERALLOW
                | RuleType.AUDITALLOW
                | RuleType.DONTAUDIT
            ):
                assert len(parts) == 4, line

                #
                # TODO: store these as and / not pairs
                # for easier matching with CIL rules
                #
                if isinstance(parts[0], list):
                    joined_parts = ' '.join(parts[0])
                    parts[0] = f'{{ {joined_parts} }}'

                if isinstance(parts[1], list):
                    joined_parts = ' '.join(parts[1])
                    target_domains = [f'{{ {joined_parts} }}']
                else:
                    target_domains = [parts[1]]

                if isinstance(parts[2], list):
                    classes = parts[2]
                else:
                    classes = [parts[2]]

                classmap.sort_classes(classes)

                varargs = list(flatten_parts(parts[3]))
                for target_domain in target_domains:
                    for class_name in classes:
                        new_parts = [parts[0]] + [target_domain, class_name]
                        classmap.sort_perms(class_name, varargs)
                        rule = Rule(rule_type, new_parts, varargs)
                        rules.append(rule)
            case RuleType.TYPE_TRANSITION:
                assert len(parts) in [4, 5], line

                if not isinstance(parts[2], list):
                    parts[2] = [parts[2]]

                varargs = parts[4:]
                parts = parts[:4]
                for class_name in parts[2]:
                    new_parts = parts[:2] + [class_name] + parts[3:]
                    rule = Rule(rule_type, new_parts, varargs)
                    rules.append(rule)
            case RuleType.ALLOWXPERM | RuleType.NEVERALLOWXPERM:
                assert len(parts) == 5
                assert parts[3] == 'ioctl'
                if not isinstance(parts[4], list):
                    parts[4] = [parts[4]]
                # TODO: remove extra zeros from ioctl numbers
                rule = Rule(rule_type, parts[:4], parts[4])
                rules.append(rule)
            case RuleType.ATTRIBUTE:
                assert len(parts) == 1, line
                rule = Rule(rule_type, parts, [])
                rules.append(rule)
            case RuleType.TYPEATTRIBUTE:
                assert len(parts) == 2, line
                rule = Rule(rule_type, parts, [])
                rules.append(rule)
            case RuleType.TYPE:
                # Convert type rules to typeattribute to allow matching
                # with split typeattributeset rules
                for t in parts[1:]:
                    rule = Rule(RuleType.TYPEATTRIBUTE, [parts[0], t], [])
                    rules.append(rule)
            case RuleType.EXPANDATTRIBUTE:
                rule = Rule(rule_type, parts, [])
                rules.append(rule)
            case _:
                assert False, line

        return rules

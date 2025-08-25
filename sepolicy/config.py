# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

# Variables extracted from system/sepolicy/build/soong/policy.go

from typing import Dict

from conditional_type import ConditionalType
from mld import MultiLevelDict
from rule import Rule, RuleType
from utils import Color, color_print

default_variables = {
    # MlsSens = 1
    'mls_num_sens': '1',
    # MlsCats = 1024
    'mls_num_cats': '1024',
    # TARGET_ARCH
    'target_arch': 'arm64',
    'target_with_asan': 'false',
    # WITH_DEXPREOPT
    'target_with_dexpreopt': 'false',
    'target_with_native_coverage': 'false',
    # TARGET_BUILD_VARIANT
    'target_build_variant': 'user',
    'target_full_treble': 'true',
    'target_compatible_property': 'true',
    # BUILD_BROKEN_TREBLE_SYSPROP_NEVERALLOW
    'target_treble_sysprop_neverallow': 'true',
    # BUILD_BROKEN_ENFORCE_SYSPROP_OWNER
    'target_enforce_sysprop_owner': 'true',
    'target_exclude_build_test': 'false',
    # PRODUCT_REQUIRES_INSECURE_EXECMEM_FOR_SWIFTSHADER
    'target_requires_insecure_execmem_for_swiftshader': 'false',
    # PRODUCT_SET_DEBUGFS_RESTRICTIONS
    'target_enforce_debugfs_restriction': 'true',
    'target_recovery': 'false',
    # BOARD_API_LEVEL
    'target_board_api_level': '202404',
}

default_variables_match_rules = {
    # public/file.te
    # type asanwrapper_exec, exec_type, file_type;
    # type rules are compiled into typeattributeset and then split by us into
    # typeattribute
    'target_with_asan': (
        Rule(
            RuleType.TYPEATTRIBUTE.value,
            ('asanwrapper_exec', 'exec_type'),
            (),
        ),
        'true',
        'false',
    ),
    # public/domain.te
    # allow domain method_trace_data_file:dir create_dir_perms;
    'target_with_native_coverage': (
        Rule(
            RuleType.ALLOW.value,
            ('domain', 'method_trace_data_file', 'dir'),
            # TODO: Try to extract the value of create_dir_perms automatically.
            # Currently it is not possible to extract these automatically because
            # the variables that we're trying to autodetect here need to be passed
            # to m4 for variable expansion, and the create_dir_perms macro is parsed
            # from the m4 result
            (
                'open',
                'getattr',
                'lock',
                'watch',
                'write',
                'watch_reads',
                'rmdir',
                'reparent',
                'ioctl',
                'remove_name',
                'add_name',
                'create',
                'rename',
                'setattr',
                'read',
                'search',
            ),
        ),
        'true',
        'false',
    ),
    # public/domain.te
    # allow domain su:fd use;
    'target_build_variant': (
        Rule(
            RuleType.ALLOW.value,
            ('allow', 'domain', 'su', 'fd'),
            ('use',),
        ),
        'userdebug',
        'user',
    ),
    # public/domain.te
    # allow domain vendor_file:dir { getattr search };
    'target_full_treble': (
        Rule(
            RuleType.ALLOW.value,
            ('domain', 'vendor_file', 'dir'),
            ('getattr', 'search'),
        ),
        'true',
        'false',
    ),
    # public/property.te
    # vendor_internal_prop(vendor_default_prop)
    # ->
    # type vendor_default_prop, property_type, vendor_property_type, vendor_internal_property_type;
    'target_compatible_property': (
        Rule(
            RuleType.TYPEATTRIBUTE.value,
            ('vendor_default_prop', 'vendor_internal_property_type'),
            (),
        ),
        'true',
        'false',
    ),
    # public/te_macros
    # system_restricted_prop(build_prop)
    # ->
    # neverallow { domain -coredomain } build_prop:property_service set;
    'target_treble_sysprop_neverallow': (
        Rule(
            RuleType.NEVERALLOW.value,
            (
                ConditionalType(
                    ['domain'],
                    ['coredomain'],
                    False,
                ),
                'build_prop',
                'property_service',
            ),
            ('set', ),
        ),
        'true',
        'false',
    ),
}


def get_default_variables(mld: MultiLevelDict[Rule]):
    variables: Dict[str, str] = default_variables.copy()

    for variable_name, data in default_variables_match_rules.items():
        rule, match_value, pass_value = data

        found = False
        for _ in mld.match(rule.hash_values):
            found = True
            break

        if found:
            variables[variable_name] = match_value
        else:
            variables[variable_name] = pass_value

        color_print(
            f'Found variable {variable_name}={variables[variable_name]}',
            color=Color.GREEN,
        )

    return variables

# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

# Variables extracted from system/sepolicy/build/soong/policy.go
default_variables = {
    'mls_num_sens': '1',
    'mls_num_cats': '1024',
    'target_arch': 'arm64',
    'target_with_asan': 'false',
    'target_with_dexpreopt': 'true',
    'target_with_native_coverage': 'false',
    'target_build_variant': 'user',
    'target_full_treble': 'true',
    'target_compatible_property': 'true',
    'target_treble_sysprop_neverallow': 'true',
    'target_enforce_sysprop_owner': 'true',
    'target_exclude_build_test': 'false',
    'target_requires_insecure_execmem_for_swiftshader': 'false',
    'target_enforce_debugfs_restriction': 'true',
    'target_recovery': 'false',
    'target_board_api_level': '202504',
}

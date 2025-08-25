# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

# Variables extracted from system/sepolicy/build/soong/policy.go
# TODO: autodetect
default_variables = {
    # MlsSens = 1
    'mls_num_sens': '1',

    # MlsCats = 1024
    'mls_num_cats': '1024',

    # TARGET_ARCH
    'target_arch': 'arm64',

    'target_with_asan': 'false',

    # WITH_DEXPREOPT
    'target_with_dexpreopt': 'true',

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

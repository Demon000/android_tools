#!/usr/bin/env python3

import sys
import os

from sepolicy_decompiler import *

if len(sys.argv) < 3:
	print(f'usage: {sys.argv[0]} <selinux_dir> <output_dir>')
	exit(1)

SELINUX_PATH = sys.argv[1]
OUTPUT_PATH = sys.argv[2]

VENDOR_CIL_FILE = 'vendor_sepolicy.cil'
VENDOR_CIL_PATH = os.path.join(SELINUX_PATH, VENDOR_CIL_FILE)

PLAT_PUB_CIL_FILE = 'plat_pub_versioned.cil'
PLAT_PUB_CIL_PATH = os.path.join(SELINUX_PATH, PLAT_PUB_CIL_FILE)

VENDOR_PROPERTY_CONTEXTS_FILE = 'vendor_property_contexts'
VENDOR_PROPERTY_CONTEXTS_PATH = os.path.join(SELINUX_PATH, VENDOR_PROPERTY_CONTEXTS_FILE)

VENDOR_FILE_CONTEXTS_FILE = 'vendor_file_contexts'
VENDOR_FILE_CONTEXTS_PATH = os.path.join(SELINUX_PATH, VENDOR_FILE_CONTEXTS_FILE)

decompiler = SepolicyDecompiler([PLAT_PUB_CIL_PATH, VENDOR_CIL_PATH],
				VENDOR_PROPERTY_CONTEXTS_PATH,
				VENDOR_FILE_CONTEXTS_PATH,
				OUTPUT_PATH)

decompiler.read_cils()
decompiler.process_macros()
decompiler.group_into_types()
decompiler.output()

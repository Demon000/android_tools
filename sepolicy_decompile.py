#!/usr/bin/env python3

import sys
import os

from sepolicy import *
from sepolicy_macros import *
from sepolicy_mld import *

VENDOR_CIL_FILE = 'vendor_sepolicy.cil'

if len(sys.argv) < 3:
	print(f'usage: {sys.argv[0]} <selinux_dir> <output_dir>')
	exit(1)

SELINUX_PATH = sys.argv[1]
OUTPUT_PATH = sys.argv[2]
VENDOR_CIL_FILE_PATH = os.path.join(SELINUX_PATH, VENDOR_CIL_FILE)

print(f'{VENDOR_CIL_FILE}: {VENDOR_CIL_FILE_PATH}')
print(f'output: {OUTPUT_PATH}')

os.makedirs(OUTPUT_PATH, exist_ok=True)

lines = []

with open(VENDOR_CIL_FILE_PATH) as f:
	lines = f.readlines()

mld = MultiLevelDict()

for line in lines:
	clean_line = line.replace('(', '') \
			 .replace(')', '') \
			 .replace('\n', '')

	parts = clean_line.split(' ')

	parts = [sanitize_type(part) for part in parts]

	rule = Rule(parts)

	mld.add(rule)

match_and_replace_macros(mld)

match = Match([])
rules = mld.get(match)

types = {}

for rule in rules:
	type_name = extract_type(rule.main_type)

	if type_name not in types:
		types[type_name] = Type(type_name)

	type = types[type_name]

	type.add_rule(rule)


for type_name in types:
	file_name = f'{type_name}.te'

	type = types[type_name]

	path = os.path.join(OUTPUT_PATH, file_name)
	with open(path, "w") as file:
		for rule in type.rules:
			s = str(rule)
			if s == '':
				continue

			file.write(str(rule))
			file.write('\n');

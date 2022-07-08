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

removed_types = {}
for type_name in types:
	if type_name in removed_types:
		continue

	type = types[type_name]

	match = Match(parts_contains=[type_name])
	rules = mld.get(match)
	main_type_name = None

	for rule in rules:
		other_type_name = extract_type(rule.main_type)
		if other_type_name == type_name:
			continue

		if main_type_name is None:
			main_type_name = other_type_name

		if other_type_name != main_type_name:
			main_type_name = None
			break

	if main_type_name is None:
		continue

	if main_type_name in removed_types:
		continue

	main_type = types[main_type_name]

	if len(type.rules) >= len(main_type.rules):
		continue

	print(f'Merging {type_name} into {main_type_name}')

	removed_types[type_name] = True

	for rule in type.rules:
		main_type.add_rule(rule)

for type_name in removed_types:
	types.pop(type_name)

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

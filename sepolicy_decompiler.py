import shutil
import sys
import os

from sepolicy import *
from sepolicy_mld import *
from sepolicy_macros import *

class SepolicyDecompiler:
	def __init__(self, cil_paths, property_contexts_path,
		     file_contexts_path, output_path):
		self.cil_paths = cil_paths
		self.property_contexts_path = property_contexts_path
		self.file_contexts_path = file_contexts_path
		self.output_path = output_path
		self.mld = MultiLevelDict()
		self.types = {}

	def read_cil_line(self, line):
		line = line.replace('(', '') \
			.replace(')', '') \
			.replace('\n', '')

		parts = line.split(' ')

		# Ignore empty lines
		if len(parts) == 1 and parts[0] == '':
			return

		parts = [sanitize_type(part) for part in parts]

		rule = Rule(parts)

		self.mld.add(rule)

	def read_cil(self, path):
		with open(path) as file:
			for line in file:
				self.read_cil_line(line)

	def read_cils(self):
		for path in self.cil_paths:
			self.read_cil(path)

	def process_macros(self):
		match_and_replace_macros(self.mld)

	def group_rule(self, rule):
		type_name = extract_type(rule.main_type)

		if type_name not in self.types:
			self.types[type_name] = Type(type_name)

		type = self.types[type_name]

		type.add_rule(rule)

	def group_into_types(self):
		match = Match([])
		rules = self.mld.get(match)

		for rule in rules:
			self.group_rule(rule)

	def output_type(self, type_name):
		type = self.types[type_name]

		file_name = f'{type_name}.te'
		path = os.path.join(self.output_path, file_name)
		with open(path, 'w') as file:
			type.write_rules_to_file(file)

	def output_types(self):
		for type_name in self.types:
			self.output_type(type_name)

	def output(self):
		os.makedirs(self.output_path, exist_ok=True)

		self.output_types()

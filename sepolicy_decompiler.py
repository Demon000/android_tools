import shutil
import sys
import os

from sepolicy import *
from sepolicy_mld import *
from sepolicy_macros import *

class SepolicyDecompiler:
	def __init__(self, cil_paths, property_contexts_path,
		     file_contexts_path, hwservice_contexts_path, output_path):
		self.cil_paths = cil_paths
		self.property_contexts_path = property_contexts_path
		self.file_contexts_path = file_contexts_path
		self.hwservice_contexts_path = hwservice_contexts_path
		self.output_path = output_path
		self.genfs_contexts_rules = []
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

		if parts[0] == 'genfscon':
			if parts[2].startswith('"') and parts[2].endswith('"'):
				parts[2] = parts[2][1:len(parts[2]) - 1]

		rule = Rule(parts)

		if parts[0] == 'genfscon':
			self.genfs_contexts_rules.append(rule)
			return

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

	def get_simple_type_filename(self, rule):
		keyword = rule.parts[0]

		file_name = None
		if  keyword == 'type':
			if 'dev_type' in rule.varargs:
				file_name = 'device'
			elif ('file_type' in rule.varargs) or ('fs_type' in rule.varargs):
				file_name = 'file'
		elif keyword.endswith('_prop'):
			file_name = 'property'

		return file_name

	def write_rule_to_file(self, rule, file):
		s = str(rule)
		if s == '':
			return

		file.write(s)
		file.write('\n');

	def write_rules_to_file(self, type, file):
		for rule in type.rules:
			self.write_rule_to_file(rule, file)

	def output_type(self, type_name):
		type = self.types[type_name]

		file_name = None

		if len(type.rules) == 1:
			rule = type.rules[0]
			file_name = self.get_simple_type_filename(rule)

		if file_name is None:
			file_name = type_name

		extension = '.te'
		file_name = file_name[:(255 - len(extension))]
		file_name += extension

		path = os.path.join(self.output_path, file_name)

		with open(path, 'a') as file:
			self.write_rules_to_file(type, file)

	def output_types(self):
		for type_name in self.types:
			self.output_type(type_name)

	def copy_contexts(self, input_path, output_path):
		lines = []
		with open(input_path, 'r') as file:
			for line in file:
				if line.startswith('#') or line == '\n':
					continue

				line = re.sub(r'\s+', ' ', line).strip() + '\n'
				lines.append(line)

		lines.sort()

		with open(output_path, 'w') as file:
			for line in lines:
				file.write(line)

	def output_property_contexts(self):
		path = os.path.join(self.output_path, 'property_contexts')
		self.copy_contexts(self.property_contexts_path, path)

	def output_file_contexts(self):
		path = os.path.join(self.output_path, 'file_contexts')
		self.copy_contexts(self.file_contexts_path, path)

	def output_hwservice_contexts(self):
		path = os.path.join(self.output_path, 'hwservice_contexts')
		shutil.copy(self.hwservice_contexts_path, path)

	def output_genfs_contexts(self):
		path = os.path.join(self.output_path, 'genfs_contexts')

		with open(path, 'w') as file:
			for rule in self.genfs_contexts_rules:
				self.write_rule_to_file(rule, file)

	def create_output_dir(self):
		os.makedirs(self.output_path, exist_ok=True)

	def clean_output_dir(self):
		for root, dirs, files in os.walk(self.output_path):
			for f in files:
				path = os.path.join(root, f)
				os.unlink(path)

			for d in dirs:
				path = os.path.join(root, d)
				shutil.rmtree(path)

	def output(self):
		self.create_output_dir()
		self.clean_output_dir()

		self.output_types()
		self.output_property_contexts()
		self.output_file_contexts()
		self.output_hwservice_contexts()
		self.output_genfs_contexts()

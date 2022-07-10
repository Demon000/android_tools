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

	def get_simple_type_filename(self, rule):
		keyword = rule.parts[0]

		file_name = None
		if  keyword == 'type':
			if 'dev_type' in rule.varargs:
				file_name = 'device.te'
			elif ('file_type' in rule.varargs) or ('sysfs_type' in rule.varargs):
				file_name = 'file.te'
		elif keyword.endswith('_prop'):
			file_name = 'property.te'

		return file_name

	def output_type(self, type_name):
		type = self.types[type_name]

		file_name = None

		if len(type.rules) == 1:
			rule = type.rules[0]
			file_name = self.get_simple_type_filename(rule)

		if file_name is None:
			file_name = f'{type_name}.te'

		path = os.path.join(self.output_path, file_name)

		with open(path, 'a') as file:
			type.write_rules_to_file(file)

	def output_types(self):
		for type_name in self.types:
			self.output_type(type_name)

	def output_property_contexts(self):
		path = os.path.join(self.output_path, 'property_contexts')
		shutil.copy(self.property_contexts_path, path)

	def output_file_contexts(self):
		path = os.path.join(self.output_path, 'file_contexts')
		shutil.copy(self.file_contexts_path, path)

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

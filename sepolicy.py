import re
import json

from sepolicy_mld import *

def typetransition_varargs_index(parts):
	l = len(parts)
	if l == 6 or l == 5:
		return l

	raise Exception(f'Invalid typetransition length: {l}, rule: {parts}')


def typeattribute_varargs_index(parts):
	l = len(parts)
	if l == 2 or l == 3:
		return l

	raise Exception(f'Invalid typeattribute length: {l}, rule: {parts}')


keyword_parts_main_type = {
	'genfscon': 5,
}


keyword_varargs_index = {
	'allow': 4,
	'allowx': 5,
	'dontaudit': 4,
	'genfscon': 8,
	'neverallow': 4,
	'roletype': 3,
	'type': 2,
	'typeattribute': typeattribute_varargs_index,
	'typeattributeset': 2,
	'typetransition': typetransition_varargs_index,
	'attribute': 2,
}


keyword_varargs_keep_order = {
	'typeattributeset': True,
}


def keep_varargs_order(parts):
	return keyword_varargs_keep_order.get(parts[0], False)


def split_varargs(parts):
	index = keyword_varargs_index.get(parts[0], 1)

	if callable(index):
		index = index(parts)

	return parts[:index], parts[index:]


def parts_main_type(parts):
	index = keyword_parts_main_type.get(parts[0], 1)

	return parts[index]


def sanitize_type(type):
	type = re.sub('_30_0$', '', type)
	return type


def format_macro(rule):
	params_str = ', '.join(rule.parts[1:])
	return f'{rule.parts[0]}({params_str})'

def join_varargs(rule):
	s = ' '.join(rule.varargs)

	if len(rule.varargs) > 1:
		s = '{ ' + s + ' }'

	return s

def format_allow(rule):
	return '{} {} {}:{} {};'.format(*rule.parts, join_varargs(rule));


def format_allowx(rule):
	return 'allowxperm {} {}:{} {} {};'.format(*rule.parts[1:], join_varargs(rule));


def format_type(rule):
	s = ', '.join(rule.varargs)
	return '{} {} {};'.format(*rule.parts, s);


def format_attribute(rule):
	return '{} {};'.format(*rule.parts)

def format_typetransition(rule):
	l = len(rule.parts)
	if l == 6:
		name = ' ' + rule.parts[4]
	else:
		name = ''
	return 'type_transition {} {}:{} {}{};'.format(*rule.parts[1:4], rule.parts[l - 1], name);


keyword_format_fn = {
	'allow': format_allow,
	'allowx': format_allowx,
	'dontaudit': format_allow,
	'neverallow': format_allow,
	'type': format_type,
	'attribute': format_attribute,
	'typetransition': format_typetransition,
}


def format_rule(rule):
	keyword = rule.parts[0]
	if keyword in keyword_format_fn:
		return keyword_format_fn[keyword](rule)

	return format_macro(rule)

class Rule:
	def __init__(self, parts, varargs=None):
		if varargs is None:
			parts, varargs = split_varargs(parts)

		if not isinstance(varargs, set) and not keep_varargs_order(parts):
			varargs = set(varargs)

		self.parts = parts
		self.varargs = varargs
		self.main_type = parts_main_type(parts)

	def __str__(self):
		return format_rule(self)


	def __eq__(self, other):
		return self.parts == other.parts and self.varargs == other.varargs


class Type:
	def __init__(self, type_name):
		self.type_name = type_name
		self.mld = MultiLevelDict()
		self.rules = []

	def __str__(self):
		s = ''
		s += f'Type: {self.type_name}\n'
		s += f'rules:\n'
		for rule in self.rules:
			s += str(rule) + '\n'
		return s

	def add_rule(self, rule):
		self.mld.add(rule)
		self.rules.append(rule)

	def get_matching(self, match):
		return self.mld.get(match)

	def reconstruct(self):
		self.mld = MultiLevelDict()
		for rule in rules:
			self.mld.add(rule)

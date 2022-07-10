import re


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
	'allowx': True,
}


def keep_varargs_order(parts):
	return keyword_varargs_keep_order.get(parts[0], False)


def split_varargs(parts):
	index = keyword_varargs_index.get(parts[0], 2)

	if callable(index):
		index = index(parts)

	return parts[:index], parts[index:]


def parts_main_type(parts):
	index = keyword_parts_main_type.get(parts[0], 1)

	return parts[index]


def sanitize_type(type):
	type = re.sub('_\d+_0$', '', type)
	return type


def extract_type(type):
	type = re.sub('^vendor_', '', type)
	type = re.sub('_exec$', '', type)
	type = re.sub('_client$', '', type)
	type = re.sub('_server$', '', type)
	type = re.sub('_default$', '', type)
	type = re.sub('_hwservice$', '', type)
	type = re.sub('_qti$', '', type)
	return type


def format_macro(rule):
	params_str = ', '.join(rule.parts[1:])
	return f'{rule.parts[0]}({params_str})'


def sort_varargs(varargs):
	if isinstance(varargs, set):
		varargs = list(varargs)

	varargs.sort()

	return varargs


def join_varargs(varargs):
	s = ' '.join(varargs)

	if len(varargs) > 1:
		s = '{ ' + s + ' }'

	return s


def format_allow(rule):
	varargs = sort_varargs(rule.varargs)
	return '{} {} {}:{} {};'.format(*rule.parts, join_varargs(varargs));


def format_allowx(rule):
	return 'allowxperm {} {}:{} {} {};'.format(*rule.parts[1:], join_varargs(rule.varargs));


def format_type(rule):
	varargs = sort_varargs(rule.varargs)
	s = ', '.join(varargs)
	return '{} {}, {};'.format(*rule.parts, s);


def format_attribute(rule):
	return '{} {};'.format(*rule.parts)


def format_typetransition(rule):
	l = len(rule.parts)
	if l == 6:
		name = ' ' + rule.parts[4]
	else:
		name = ''
	return 'type_transition {} {}:{} {}{};'.format(*rule.parts[1:4], rule.parts[l - 1], name);


def format_permissive(rule):
	return 'permissive {};'.format(rule.parts[1])


def format_noop(rule):
	return ''


keyword_format_fn = {
	'allow': format_allow,
	'allowx': format_allowx,
	'dontaudit': format_allow,
	'neverallow': format_allow,
	'type': format_type,
	'attribute': format_attribute,
	'typetransition': format_typetransition,
	'genfscon': format_noop,
	'typepermissive': format_permissive,
}


def format_rule(rule):
	keyword = rule.parts[0]
	if keyword in keyword_format_fn:
		return keyword_format_fn[keyword](rule)

	return format_macro(rule)


class Rule:
	def __init__(self, parts, varargs=None, main_type=None):
		if varargs is None:
			parts, varargs = split_varargs(parts)

		if not isinstance(varargs, set) and not keep_varargs_order(parts):
			varargs = set(varargs)

		if main_type is None:
			main_type = parts_main_type(parts)

		self.parts = parts
		self.varargs = varargs
		self.main_type = main_type

	def __str__(self):
		return format_rule(self)

	def __eq__(self, other):
		return self.parts == other.parts and self.varargs == other.varargs


class Type:
	def __init__(self, type_name):
		self.type_name = type_name
		self.rules = []

	def add_rule(self, rule):
		self.rules.append(rule)

	def write_rule_to_file(self, rule, file):
		s = str(rule)
		if s == '':
			return

		file.write(s)
		file.write('\n');

	def write_rules_to_file(self, file):
		for rule in self.rules:
			self.write_rule_to_file(rule, file)

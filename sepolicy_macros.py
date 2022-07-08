from sepolicy import *
from sepolicy_macro import *
from sepolicy_matches import *


# Files
x_file_perms = ['getattr', 'execute', 'execute_no_trans', 'map']
r_file_perms = ['getattr', 'open', 'read', 'ioctl', 'lock', 'map', 'watch', 'watch_reads']
w_file_perms = ['open', 'append', 'write', 'lock', 'map']
rx_file_perms = r_file_perms + x_file_perms
ra_file_perms = r_file_perms + ['append']
rw_file_perms = r_file_perms + w_file_perms
rwx_file_perms = rw_file_perms + x_file_perms
create_file_perms = ['create', 'rename', 'setattr', 'unlink'] + rw_file_perms

# Dirs
w_dir_perms = ['open', 'search', 'write', 'add_name', 'remove_name', 'lock']
r_dir_perms = ['open', 'getattr', 'read', 'search', 'ioctl', 'lock', 'watch', 'watch_reads']
ra_dir_perms = r_dir_perms + ['add_name', 'write']
rw_dir_perms = r_dir_perms + w_dir_perms
create_dir_perms = ['create', 'reparent', 'rename', 'rmdir', 'setattr'] + rw_dir_perms

# IPC
w_ipc_perms = ['write', 'unix_write']
r_ipc_perms = ['getattr', 'read', 'associate', 'unix_read']
rw_ipc_perms = r_ipc_perms + w_ipc_perms
create_ipc_perms = ['create', 'setattr', 'destroy'] + rw_ipc_perms

# Sockets
rw_socket_perms_no_ioctl = ['read', 'getattr', 'write', 'setattr', 'lock', 'append', 'bind', 'connect', 'getopt', 'setopt', 'shutdown', 'map']
rw_socket_perms = ['ioctl']  + rw_socket_perms_no_ioctl

create_socket_perms_no_ioctl = ['create'] + rw_socket_perms_no_ioctl
create_socket_perms = ['create'] + rw_socket_perms

rw_stream_socket_perms = rw_socket_perms + ['listen', 'accept']
create_stream_socket_perms = ['create'] + rw_stream_socket_perms

allow_permission_macro_names = [
	'create_stream_socket_perms',
	'rw_stream_socket_perms',
	'create_socket_perms',
	'create_socket_perms_no_ioctl',
	'rw_socket_perms',
	'rw_socket_perms_no_ioctl',
	'create_ipc_perms',
	'rw_ipc_perms',
	'r_ipc_perms',
	'w_ipc_perms',
	'create_dir_perms',
	'rw_dir_perms',
	'ra_dir_perms',
	'r_dir_perms',
	'w_dir_perms',
	'create_file_perms',
	'rwx_file_perms',
	'rw_file_perms',
	'ra_file_perms',
	'rx_file_perms',
	'w_file_perms',
	'r_file_perms',
	'x_file_perms',
]


no_w_file_perms = ['append', 'create', 'link', 'unlink', 'relabelfrom', 'rename', 'setattr', 'write']
no_rw_file_perms = no_w_file_perms + ['open', 'read', 'ioctl', 'lock', 'watch', 'watch_mount', 'watch_sb', 'watch_with_perm', 'watch_reads']
no_x_file_perms = ['execute', 'execute_no_trans']
no_w_dir_perms = ['add_name', 'create', 'link', 'relabelfrom', 'remove_name', 'rename', 'reparent', 'rmdir', 'setattr', 'write']

neverallow_permission_macro_names = [
	'no_w_dir_perms',
	'no_x_file_perms',
	'no_rw_file_perms',
	'no_w_file_perms',
]


def replace_permissions_macro(mld, macro, rule, matched_types):
	match = macro.matches[0]
	contains = match.contains
	rule.varargs = rule.varargs.difference(contains)
	rule.varargs.add(macro.name)


allow_permission_macros = []
for macro_name in allow_permission_macro_names:
	subset = globals()[macro_name]
	match = Match(['allow'], contains=subset)
	macro = Macro(macro_name, match, replace_permissions_macro)
	allow_permission_macros.append(macro)

neverallow_permission_macros = []
for macro_name in neverallow_permission_macro_names:
	subset = globals()[macro_name]
	match = Match(['neverallow'], contains=subset)
	macro = Macro(macro_name, match, replace_permissions_macro)
	neverallow_permission_macros.append(macro)


def replace_named_macro(mld, macro, rules, matched_types):
	for rule in rules:
		mld.remove(rule)

	rule = Rule([macro.name] + matched_types, [])
	mld.add(rule)


def remove_rule(mld, macro, rule, matched_types):
	mld.remove(rule)


def remove_rules(mld, macro, rules, matched_types):
	for rule in rules:
		mld.remove(rule)


def replace_typeattribute(mld, macro, rule, matched_types):
	mld.remove(rule)

	rule = Rule([macro.name, rule.parts[1]])
	mld.add(rule)


def replace_typeattribute_with_type(mld, macro, rules, matched_types):
	assert len(rules) == 1

	rule = rules[0]

	mld.remove(rule)

	type = matched_types[0]
	attr_type = matched_types[1]
	match_type = Match(['type', type])
	rule = mld.get_one(match_type)
	if rule is None:
		rule = Rule(['type', type])
		mld.add(rule)

	rule.varargs.add(attr_type)


def replace_typeattributeset_base_typeattr(mld, rule):
	try:
		and_index = rule.varargs.index('and')
	except ValueError:
		and_index = 0

	try:
		not_index = rule.varargs.index('not')
	except ValueError:
		not_index = 0

	and_tokens = rule.varargs[and_index + 1:not_index]
	not_tokens = rule.varargs[not_index + 1:]

	type_str = ''
	type_str += '{'

	if and_tokens:
		type_str += ' '
		type_str += ' '.join(and_tokens)

	if not_tokens:
		type_str += ' -'
		type_str += ' -'.join(not_tokens)

	type_str += ' }'

	type = rule.parts[1]

	match = Match(parts_contains=[type])
	rules = mld.get(match)

	for rule in rules:
		mld.remove(rule)
		for i in range(len(rule.parts)):
			if rule.parts[i] == type:
				rule.parts[i] = type_str
		mld.add(rule)


def replace_typeattributeset(mld, macro, rule, matched_types):
	mld.remove(rule)

	if rule.parts[1].startswith('base_typeattr_'):
		replace_typeattributeset_base_typeattr(mld, rule)
		return

	for type in rule.varargs:
		typeattribute_rule = Rule(['typeattribute', type, rule.parts[1]])
		mld.add(typeattribute_rule)


def define_prop_macro(owner, scope):
	return 	Macro(
		f'{owner}_{scope}_prop',
		[
			Match(['typeattribute', '$1', 'property_type']),
			Match(['typeattribute', '$1', f'{owner}_property_type']),
			Match(['typeattribute', '$1', f'{owner}_{scope}_property_type']),
		],
		replace_fn=replace_named_macro,
	)

macros = [
	# Not used for anything
	Macro(
		'remove roletype',
		[
			Match(['roletype']),
		],
		replace_fn=remove_rule,
	),

	# Will be recreated based on leftover typeattributes
	Macro(
		'remove type',
		[
			Match(['type']),
		],
		replace_fn=remove_rule,
	),

	Macro(
		'remove base_typeattr_ attribute leftovers',
		[
			Match(['typeattribute', 'base_typeattr_$1']),
		],
		replace_fn=remove_rules,
	),

	*allow_permission_macros,
	*neverallow_permission_macros,

	# Rename typeattribute to attribute to match written sepolicy
	Macro(
		'attribute',
		[
			Match(['typeattribute', '$1']),
		],
		replace_fn=replace_named_macro,
	),

	Macro(
		'split typeattributeset',
		[
			Match(['typeattributeset']),
		],
		replace_fn=replace_typeattributeset,
	),

	# Normal macros follow
	Macro(
		'domain_trans',
		[
			Match(['allow', '$1', '$2', 'file'], equal=['getattr', 'open', 'read', 'execute', 'map']),
			Match(['allow', '$1', '$3', 'process'], equal=['transition']),
			Match(['allow', '$3', '$2', 'file'], equal=['entrypoint', 'open', 'read', 'execute', 'getattr', 'map']),
			Match(['dontaudit', '$1', '$3', 'process'], equal=['noatsecure']),
			Match(['allow', '$1', '$3', 'process'], equal=['siginh', 'rlimitinh']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'domain_auto_trans',
		[
			Match(['domain_trans', '$1', '$2', '$3']),
			Match(['typetransition', '$1', '$2', 'process', '$3']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'file_type_trans',
		[
			Match(['allow', '$1', '$2', 'dir'], equal=['ra_dir_perms']),
			Match(['allow', '$1', '$3', 'file'], equal=['create_file_perms']),
			Match(['allow', '$1', '$3', 'lnk_file'], equal=['create_file_perms']),
			Match(['allow', '$1', '$3', 'sock_file'], equal=['create_file_perms']),
			Match(['allow', '$1', '$3', 'fifo_file'], equal=['create_file_perms']),
			Match(['allow', '$1', '$3', 'dir'], equal=['create_dir_perms']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'file_type_auto_trans',
		[
			Match(['file_type_trans', '$1', '$2', '$3']),
			Match(['typetransition', '$1', '$2', 'dir', '$3']),
			Match(['typetransition', '$1', '$2', 'file', '$3']),
			Match(['typetransition', '$1', '$2', 'lnk_file', '$3']),
			Match(['typetransition', '$1', '$2', 'sock_file', '$3']),
			Match(['typetransition', '$1', '$2', 'fifo_file', '$3']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'init_daemon_domain',
		[
			Match(['domain_auto_trans', 'init', '$1_exec', '$1']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'r_dir_file',
		[
			Match(['allow', '$1', '$2', 'dir'], equal=['r_dir_perms']),
			Match(['allow', '$1', '$2', 'file'], equal=['r_file_perms']),
			Match(['allow', '$1', '$2', 'lnk_file'], equal=['r_file_perms']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'unix_socket_connect',
		[
			Match(['allow', '$1', '$2_socket', 'sock_file'], equal=['write']),
			Match(['allow', '$1', '$3', 'unix_stream_socket'], equal=['connectto']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'unix_socket_send',
		[
			Match(['allow', '$1', '$2_socket', 'sock_file'], equal=['write']),
			Match(['allow', '$1', '$3', 'unix_dgram_socket'], equal=['sendto']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'get_prop',
		[
			Match(['allow', '$1', '$2', 'file'], equal=['getattr', 'open', 'read', 'map']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'set_prop',
		[
			Match(['allow', '$1', '$2', 'property_service'], equal=['set']),
			Match(['get_prop', '$1', '$2']),
		],
		replace_fn=replace_named_macro,
	),
	# Will only appear once for all set_prop calls, remove it afterwards
	Macro(
		'remove set_prop common pieces',
		[
			Match(['unix_socket_connect', '$1', 'property', 'init']),
		],
		replace_fn=remove_rules,
	),

	Macro(
		'binder_service',
		[
			Match(['typeattribute', '$1', 'binderservicedomain']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'binder_use',
		[
			Match(['allow', '$1', 'servicemanager', 'binder'], equal=['call', 'transfer']),
			Match(['allow', 'servicemanager', '$1', 'binder'], equal=['call', 'transfer']),
			Match(['allow', 'servicemanager', '$1', 'dir'], equal=['search']),
			Match(['allow', 'servicemanager', '$1', 'file'], equal=['read', 'open']),
			Match(['allow', 'servicemanager', '$1', 'process'], equal=['getattr']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'hwbinder_use',
		[
			Match(['allow', '$1', 'hwservicemanager', 'binder'], equal=['call', 'transfer']),
			Match(['allow', 'hwservicemanager', '$1', 'binder'], equal=['call', 'transfer']),
			Match(['allow', 'hwservicemanager', '$1', 'dir'], equal=['search']),
			Match(['allow', 'hwservicemanager', '$1', 'file'], equal=['read', 'open', 'map']),
			Match(['allow', 'hwservicemanager', '$1', 'process'], equal=['getattr']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'vndbinder_use',
		[
			Match(['allow', '$1', 'vndbinder_device', 'chr_file'], equal=['rw_file_perms']),
			Match(['allow', '$1', 'vndservicemanager', 'binder'], equal=['call', 'transfer']),
			Match(['allow', 'vndservicemanager', '$1', 'dir'], equal=['search']),
			Match(['allow', 'vndservicemanager', '$1', 'file'], equal=['read', 'open', 'map']),
			Match(['allow', 'vndservicemanager', '$1', 'process'], equal=['getattr']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'binder_call',
		[
			Match(['allow', '$1', '$2', 'binder'], equal=['call', 'transfer']),
			Match(['allow', '$2', '$1', 'binder'], equal=['transfer']),
			Match(['allow', '$1', '$2', 'fd'], equal=['use']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'wakelock_use',
		[
			Match(['allow', '$1', 'sysfs_wake_lock', 'file'], equal=['rw_file_perms']),
			Match(['allow', '$1', 'self', 'capability2'], equal=['block_suspend']),
			Match(['allow', '$1', 'self', 'cap2_userns'], equal=['block_suspend']),
			Match(['binder_call', '$1', 'system_suspend_server']),
			Match(['allow', '$1', 'system_suspend_hwservice', 'hwservice_manager'], equal=['find']),
			Match(['hwbinder_use', '$1']),
			Match(['get_prop', '$1', 'hwservicemanager_prop']),
			Match(['allow', '$1', 'hidl_manager_hwservice', 'hwservice_manager'], equal=['find']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'app_domain',
		[
			Match(['typeattribute', '$1', 'appdomain']),
			Match(['typetransition', '$1', 'tmpfs', 'file', 'appdomain_tmpfs']),
			Match(['allow', '$1', 'appdomain_tmpfs', 'file'], equal=['execute', 'getattr', 'map', 'read', 'write']),
			Match(['neverallow', '{ $1 -runas_app -shell -simpleperf }', '{ domain -$1 }', 'file'], equal=['no_rw_file_perms']),
			Match(['neverallow', '{ appdomain -runas_app -shell -simpleperf -$1 }', '$1', 'file'], equal=['no_rw_file_perms']),
			Match(['neverallow', '{ domain -crash_dump -runas_app -simpleperf -$1 }', '$1', 'process'], equal=['ptrace']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'net_domain',
		[
			Match(['typeattribute', '$1', 'netdomain']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'hal_attribute',
		[
			Match(['attribute', 'hal_$1']),
			Match(['attribute', 'hal_$1_client']),
			Match(['attribute', 'hal_$1_server']),
		],
		replace_fn=replace_named_macro,
	),

	Macro(
		'hal_server_domain',
		[
			Match(['typeattribute', '$1', '$2_server']),
			Match(['typeattribute', '$1', '$2']),
		],
		replace_fn=replace_named_macro,
	),
	# Will only appear once for all hal_server_domain calls, remove it afterwards
	Macro(
		'remove hal_server_domain common pieces',
		[
			Match(['typeattribute', '$1', 'halserverdomain']),
		],
		replace_fn=remove_rules,
	),

	Macro(
		'passthrough_hal_client_domain',
		[
			Match(['typeattribute', '$1', '$2_client']),
			Match(['typeattribute', '$1', '$2']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'hal_client_domain',
		[
			Match(['typeattribute', '$1', '$2_client']),
		],
		replace_fn=replace_named_macro,
	),
	# Will only appear once for all hal_client_domain or
	# passthrough_hal_client_domain calls, remove it afterwards
	Macro(
		'remove hal_client_domain common pieces',
		[
			Match(['typeattribute', '$1', 'halclientdomain']),
		],
		replace_fn=remove_rules,
	),

	Macro(
		'add_service',
		[
			Match(['allow', '$1', '$2', 'service_manager'], equal=['add', 'find']),
			Match(['neverallow', '{ domain -$1 }', '$2', 'service_manager'], equal=['add']),
		],
		replace_fn=replace_named_macro,
	),

	Macro(
		'add_hwservice',
		[
			Match(['allow', '$1', '$2', 'hwservice_manager'], equal=['add', 'find']),
			Match(['neverallow', '{ domain -$1 }', '$2', 'hwservice_manager'], equal=['add']),
		],
		replace_fn=replace_named_macro,
	),
	# Will only appear once for all add_hwservice calls, remove it afterwards
	Macro(
		'remove add_hwservice common pieces',
		[
			Match(['allow', '$1', 'hidl_base_hwservice', 'hwservice_manager'], equal=['add']),
		],
		replace_fn=remove_rules,
	),

	Macro(
		'hal_attribute_service',
		[
			Match(['allow', '$1_client', '$2', 'service_manager'], equal=['find']),
			Match(['add_service', '$1_server', '$2']),
		],
		replace_fn=replace_named_macro,
	),
	Macro(
		'hal_attribute_hwservice',
		[
			Match(['allow', '$1_client', '$2', 'hwservice_manager'], equal=['find']),
			Match(['add_hwservice', '$1_server', '$2']),
			Match(['neverallow', '{ domain -$1_client -$1_server }', '$2', 'hwservice_manager'], equal=['find']),
		],
		replace_fn=replace_named_macro,
	),

	define_prop_macro('system', 'internal'),
	define_prop_macro('system', 'restricted'),
	define_prop_macro('system', 'public'),
	define_prop_macro('product', 'internal'),
	define_prop_macro('product', 'restricted'),
	define_prop_macro('product', 'public'),
	define_prop_macro('vendor', 'internal'),
	define_prop_macro('vendor', 'restricted'),
	define_prop_macro('vendor', 'public'),

	Macro(
		'system_vendor_config_prop',
		[
			Match(['system_public_prop', '$1']),
			Match(['set_prop', 'vendor_init', '$1']),
		],
	),

	# Form a type statement from leftover typeattributes
	Macro(
		'type',
		[
			Match(['typeattribute', '$1', '$2']),
		],
		replace_fn=replace_typeattribute_with_type,
	),
]


def add_matched_types(prev_partial_matched_types, new_partial_matched_types, fully_matched_types, matched_types):
	new_merged_types = []

	for m in prev_partial_matched_types:
		if m == matched_types:
			return

		assert len(m) == len(matched_types)

		merged_types = []
		any_added = False
		for i in range(len(m)):
			original_type = m[i]
			new_type = matched_types[i]

			if original_type is not None and \
				new_type is not None and \
				original_type != new_type:
				break

			chosen_type = new_type or original_type
			merged_types.append(chosen_type)

		if len(merged_types) != len(m):
			continue

		new_merged_types.append(merged_types)

	new_merged_types.append(matched_types)

	for m in new_merged_types:
		if None in m:
			new_partial_matched_types.append(m)
		else:
			fully_matched_types.append(m)

def extend_matched_types(macro, matched_types):
	for i in range(len(matched_types), macro.max_index + 1):
		matched_types.append(None)

def match_and_replace_macro(mld, macro):
	prev_partial_matched_types = []
	new_partial_matched_types = []
	fully_matched_types = []

	for match in macro.matches:
		rules = mld.get(match)

		for rule in rules:
			if macro.max_index is None:
				# No index tracking, just replace now
				macro.replace_fn(mld, macro, rule, [])
				continue

			rule_matched_types = match.extract_matched_indices(rule)
			extend_matched_types(macro, rule_matched_types)
			add_matched_types(prev_partial_matched_types, new_partial_matched_types,
				fully_matched_types, rule_matched_types)

		prev_partial_matched_types.extend(new_partial_matched_types)
		new_partial_matched_types = []

	for m in fully_matched_types:
		filled_macro = macro.fill_matched_indices(m)
		matched_rules = []
		missing = False

		for match in filled_macro.matches:
			rule = mld.get_one(match)
			if rule is None:
				missing = True
				break

			matched_rules.append(rule)

		if missing:
			continue

		filled_macro.replace_fn(mld, filled_macro, matched_rules, m)


def match_and_replace_macros(mld):
	for macro in macros:
		print(f'Processing macro {macro.name}...')
		match_and_replace_macro(mld, macro)

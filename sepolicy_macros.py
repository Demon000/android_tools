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
rw_socket_perms_no_ioctl = ['read', 'getattr', 'write', 'setattr', 'lock', 'append', 'bind', 'connect', 'getopt',
			    'setopt', 'shutdown', 'map']
rw_socket_perms = ['ioctl'] + rw_socket_perms_no_ioctl

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
no_rw_file_perms = no_w_file_perms + ['open', 'read', 'ioctl', 'lock', 'watch', 'watch_mount', 'watch_sb',
				      'watch_with_perm', 'watch_reads']
no_x_file_perms = ['execute', 'execute_no_trans']
no_w_dir_perms = ['add_name', 'create', 'link', 'relabelfrom', 'remove_name', 'rename', 'reparent', 'rmdir', 'setattr',
		  'write']

fd_perms = ['use']
peer_perms = ['recv']
memprotect_perms = ['mmap_zero']

netif_perms = ['egress', 'ingress']
packet_perms = ['forward_in', 'forward_out', 'recv', 'relabelto', 'send']
association_perms = ['polmatch', 'recvfrom', 'sendto', 'setcontext']
bpf_perms = ['map_create', 'map_read', 'map_write', 'prog_load', 'prog_run']
perf_event_perms = ['cpu', 'kernel', 'open', 'read', 'tracepoint', 'write']
filesystem_perms = ['associate', 'getattr', 'mount', 'quotaget', 'quotamod', 'relabelfrom', 'relabelto', 'remount', 'unmount', 'watch']

common_file_perms = ['append', 'audit_access', 'create', 'execute', 'execmod', 'getattr', 'ioctl', 'link', 'lock', 'map',
		     'mounton', 'open', 'quotaon', 'read', 'relabelfrom', 'relabelto', 'rename', 'setattr', 'unlink',
		     'watch', 'watch_mount', 'watch_sb', 'watch_with_perm', 'watch_reads', 'write']
dir_perms = common_file_perms + ['add_name', 'remove_name', 'reparent', 'rmdir', 'search']
file_perms = common_file_perms + ['entrypoint', 'execute_no_trans']

common_socket_perms = ['accept', 'append', 'bind', 'connect', 'create', 'getattr', 'getopt', 'ioctl', 'listen', 'lock',
		       'map', 'name_bind', 'read', 'recvfrom', 'relabelfrom', 'relabelto', 'sendto', 'setattr', 'setopt',
		       'shutdown', 'write']
tcp_socket_perms = common_socket_perms + ['name_connect', 'node_bind']
icmp_socket_perms = common_socket_perms + ['node_bind']
sctp_socket_perms = tcp_socket_perms + ['association']
unix_stream_socket_perms = common_socket_perms + ['connectto']
tun_socket_perms = common_socket_perms + ['attach_queue']
netlink_xfrm_socket_perms = common_socket_perms + ['nlmsg_read', 'nlmsg_write']
netlink_audit_socket_perms = netlink_xfrm_socket_perms + ['nlmsg_readpriv', 'nlmsg_relay', 'nlmsg_tty_audit']

ipc_perms = ['associate', 'create', 'destroy', 'getattr', 'read', 'setattr', 'unix_read', 'unix_write', 'write']
msgq_perms = ipc_perms + ['enqueue']
msg_perms = ipc_perms + ['send', 'receive']
shm_perms = ipc_perms + ['lock']

process_perms = ['dyntransition', 'execheap', 'execmem', 'execstack', 'fork', 'getattr', 'getcap', 'getpgid', 'getsched',
		 'getsession', 'getrlimit', 'noatsecure', 'ptrace', 'rlimitinh', 'setcap', 'setcurrent', 'setexec',
		 'setfscreate', 'setkeycreate', 'setpgid', 'setrlimit', 'setsched', 'setsockcreate', 'share', 'sigchld',
		 'siginh', 'sigkill', 'signal', 'signull', 'sigstop', 'transition']
process2_perms = ['nnp_transition', 'nosuid_transition']

capability_perms = ['audit_write', 'chown', 'dac_override', 'dac_read_search', 'fowner', 'fsetid', 'ipc_lock', 'ipc_owner',
		    'kill', 'lease', 'linux_immutable', 'mknod', 'net_admin', 'net_bind_service', 'net_raw', 'netbroadcast',
		    'setfcap', 'setgid', 'setpcap', 'setuid', 'sys_admin', 'sys_boot', 'sys_chroot', 'sys_module', 'sys_nice',
		    'sys_pacct', 'sys_ptrace', 'sys_rawio', 'sys_resource', 'sys_time', 'sys_tty_config']
capability2_perms = ['audit_read', 'bpf', 'block_suspend', 'mac_admin', 'mac_override', 'perfmon', 'syslog', 'wake_alarm']

cap_userns_perms = ['audit_write', 'chown', 'dac_override', 'dac_read_search', 'fowner', 'fsetid', 'ipc_lock', 'ipc_owner', 'kill',
	      'lease', 'linux_immutable', 'mknod', 'net_admin', 'net_bind_service', 'net_raw', 'netbroadcast', 'setfcap',
	      'setgid', 'setpcap', 'setuid', 'sys_admin', 'sys_boot', 'sys_chroot', 'sys_module', 'sys_nice', 'sys_pacct',
	      'sys_ptrace', 'sys_rawio', 'sys_resource', 'sys_time', 'sys_tty_config']
cap2_userns_perms = ['audit_read', 'bpf', 'block_suspend', 'mac_admin', 'mac_override', 'perfmon', 'syslog', 'wake_alarm']

security_perms = ['check_context', 'compute_av', 'compute_create', 'compute_member', 'compute_relabel', 'compute_user',
		  'load_policy', 'read_policy', 'setbool', 'setcheckreqprot', 'setenforce', 'setsecparam', 'validate_trans']

system_perms = ['ipc_info', 'module_load', 'module_request', 'syslog_console', 'syslog_mod', 'syslog_read']
binder_perms = ['call', 'impersonate', 'set_context_mgr', 'transfer']

all_perms_types = {
	'fd': fd_perms,
	'peer': peer_perms,
	'memprotect': memprotect_perms,
	'netif': netif_perms,
	'packet': packet_perms,
	'association': association_perms,
	'bpf': bpf_perms,
	'perf_event': perf_event_perms,
	'filesystem': filesystem_perms,

	'lnk_file': common_file_perms,
	'chr_file': common_file_perms,
	'blk_file': common_file_perms,
	'sock_file': common_file_perms,
	'fifo_file': common_file_perms,
	'anon_inode': common_file_perms,
	'dir': dir_perms,
	'file': file_perms,

	'socket': common_socket_perms,
	'packet_socket': common_socket_perms,
	'unix_dgram_socket': common_socket_perms,
	'key_socket': common_socket_perms,
	'netlink_socket': common_socket_perms,
	'netlink_nflog_socket': common_socket_perms,
	'netlink_selinux_socket': common_socket_perms,
	'netlink_dnrt_socket': common_socket_perms,
	'netlink_kobject_uevent_socket': common_socket_perms,
	'netlink_iscsi_socket': common_socket_perms,
	'netlink_fib_lookup_socket': common_socket_perms,
	'netlink_connector_socket': common_socket_perms,
	'netlink_netfilter_socket': common_socket_perms,
	'netlink_generic_socket': common_socket_perms,
	'netlink_scsitransport_socket': common_socket_perms,
	'netlink_rdma_socket': common_socket_perms,
	'netlink_crypto_socket': common_socket_perms,
	'appletalk_socket': common_socket_perms,

	'ax25_socket': common_socket_perms,
	'ipx_socket': common_socket_perms,
	'netrom_socket': common_socket_perms,
	'atmpvc_socket': common_socket_perms,
	'x25_socket': common_socket_perms,
	'rose_socket': common_socket_perms,
	'decnet_socket': common_socket_perms,
	'atmsvc_socket': common_socket_perms,
	'rds_socket': common_socket_perms,
	'irda_socket': common_socket_perms,
	'pppox_socket': common_socket_perms,
	'llc_socket': common_socket_perms,
	'can_socket': common_socket_perms,
	'tipc_socket': common_socket_perms,
	'bluetooth_socket': common_socket_perms,
	'iucv_socket': common_socket_perms,
	'rxrpc_socket': common_socket_perms,
	'isdn_socket': common_socket_perms,
	'phonet_socket': common_socket_perms,
	'ieee802154_socket': common_socket_perms,
	'caif_socket': common_socket_perms,
	'alg_socket': common_socket_perms,
	'nfc_socket': common_socket_perms,
	'vsock_socket': common_socket_perms,
	'kcm_socket': common_socket_perms,
	'qipcrtr_socket': common_socket_perms,
	'smc_socket': common_socket_perms,
	'xdp_socket': common_socket_perms,

	'tcp_socket': tcp_socket_perms,
	'udp_socket': tcp_socket_perms,
	'rawip_socket': tcp_socket_perms,
	'dccp_socket': tcp_socket_perms,
	'unix_stream_socket': unix_stream_socket_perms,
	'tun_socket': tun_socket_perms,
	'netlink_xfrm_socket': netlink_xfrm_socket_perms,
	'netlink_route_socket': netlink_xfrm_socket_perms,
	'netlink_firewall_socket': netlink_xfrm_socket_perms,
	'netlink_tcpdiag_socket': netlink_xfrm_socket_perms,
	'netlink_ip6fw_socket': netlink_xfrm_socket_perms,
	'netlink_audit_socket': netlink_audit_socket_perms,
	'sctp_socket': sctp_socket_perms,
	'icmp_socket': icmp_socket_perms,

	'ipc': ipc_perms,
	'sem': ipc_perms,
	'msgq': msgq_perms,
	'msg': msg_perms,
	'shm': shm_perms,

	'process': process_perms,
	'process2': process2_perms,
	'capability': capability2_perms,
	'capability2': capability2_perms,
	'cap_userns': cap_userns_perms,
	'cap2_userns': cap2_userns_perms,

	'security': security_perms,
	'system': system_perms,
}

neverallow_permission_macro_names = [
	'no_w_dir_perms',
	'no_x_file_perms',
	'no_rw_file_perms',
	'no_w_file_perms',
]


def replace_permissions_macro(mld, match_result):
	rules = match_result.rules

	assert len(rules) == 1

	rule = rules[0]

	macro = match_result.filled_macro
	match = macro.matches[0]
	contains = match.contains
	rule.varargs = rule.varargs.difference(contains)
	rule.varargs.add(macro.name)


allow_permission_macros = []
neverallow_permission_macros = []

def add_perms_to(keyword, names, macros):
	for macro_name in names:
		subset = globals()[macro_name]
		match = Match([keyword], contains=subset)
		macro = Macro(macro_name, match, replace_permissions_macro)
		macros.append(macro)

def add_all_perms_to(keyword, macros):
	for type in all_perms_types:
		perms = all_perms_types[type]
		match = Match([keyword, '$1', '$2', type], contains=perms)
		macro = Macro('*', match, replace_permissions_macro)
		macros.append(macro)

add_all_perms_to('allow', allow_permission_macros)
add_perms_to('allow', allow_permission_macro_names, allow_permission_macros)

add_all_perms_to('neverallow', neverallow_permission_macros)
add_perms_to('neverallow', neverallow_permission_macro_names, neverallow_permission_macros)


def replace_named_macro(mld, match_result):
	replace_result = MacroReplaceResult()

	rules = match_result.rules
	matched_types = match_result.types
	macro = match_result.filled_macro
	main_type = None

	for rule in rules:
		if rule is None:
			continue

		if rule.parts[1] == matched_types[0]:
			main_type = rule.main_type

		replace_result.removed.append(rule)

	rule = Rule([macro.name] + matched_types, [], main_type=main_type)
	replace_result.added.append(rule)

	return replace_result


def remove_rules(mld, match_result):
	replace_result = MacroReplaceResult()

	rules = match_result.rules

	for rule in rules:
		replace_result.removed.append(rule)

	return replace_result


def replace_typeattribute(mld, match_result):
	replace_result = MacroReplaceResult()

	rules = match_result.rules
	macro = match_result.filled_macro

	assert len(rules) == 1

	rule = rules[0]

	replace_result.removed.append(rule)

	rule = Rule([macro.name, rule.parts[1]])
	replace_result.added.append(rule)

	return replace_result


def replace_typeattribute_with_type(mld, match_result):
	rules = match_result.rules

	assert len(rules) == 1

	rule = rules[0]

	mld.remove(rule)

	matched_types = match_result.types
	type = matched_types[0]
	attr_type = matched_types[1]
	match_type = Match(['type', type])
	rule = mld.get_one(match_type)
	if rule is None:
		rule = Rule(['type', type])
		mld.add(rule)

	rule.varargs.add(attr_type)

	match_attributre = Match(['attribute', type])
	rule = mld.get_one(match_attributre)
	if rule is not None:
		mld.remove(rule)


def construct_expanded_base_typeattr(rule):
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
	and_tokens_len = len(and_tokens)
	not_tokens_len = len(not_tokens)

	type_str = ''

	if not and_tokens_len and not_tokens_len:
		type_str += '~'

		if not_tokens_len != 1:
			type_str += '{'
			type_str += ' '

		type_str += ' '.join(not_tokens)

		if not_tokens_len != 1:
			type_str += ' }'
	elif and_tokens_len and not_tokens_len:
		type_str += '{'

		type_str += ' '
		type_str += ' '.join(and_tokens)

		type_str += ' -'
		type_str += ' -'.join(not_tokens)

		type_str += ' }'
	else:
		raise Exception(f'Unhandled base type {rule}')

	return type_str

def replace_typeattributeset_base_typeattr(mld, match_result):
	rules = match_result.rules

	assert len(rules) == 1

	rule = rules[0]

	if len(rule.varargs) == 1 and rule.varargs[0] == 'all':
		type_str = '*'
	else:
		type_str = construct_expanded_base_typeattr(rule)

	type = rule.parts[1]

	mld.remove(rule)

	match = Match(parts_contains=[type])
	rules = mld.get(match)

	for rule in rules:
		mld.remove(rule)
		new_parts = []
		for part in rule.parts:
			if part == type:
				part = type_str

			new_parts.append(part)

		new_rule = Rule(new_parts, rule.varargs, main_type=type)
		mld.add(new_rule)

def replace_typeattributeset(mld, match_result):
	replace_result = MacroReplaceResult()

	rules = match_result.rules

	assert len(rules) == 1

	rule = rules[0]

	replace_result.removed.append(rule)

	for type in rule.varargs:
		typeattribute_rule = Rule(['typeattribute', type, rule.parts[1]])
		replace_result.added.append(typeattribute_rule)

	return replace_result


def define_prop_macro(owner, scope):
	return Macro(
		f'{owner}_{scope}_prop',
		[
			Match(['type', '$1'], equal=['property_type', f'{owner}_property_type', f'{owner}_{scope}_property_type']),
		],
		replace_named_macro,
	)


macros = [
	# Not used for anything
	Macro(
		'remove roletype',
		[
			Match(['roletype']),
		],
		remove_rules,
	),

	# Will be recreated based on leftover typeattributes
	Macro(
		'remove type',
		[
			Match(['type']),
		],
		remove_rules,
	),

	Macro(
		'remove base_typeattr_ attribute leftovers',
		[
			Match(['typeattribute', 'base_typeattr_$1']),
		],
		remove_rules,
	),

	*allow_permission_macros,
	*neverallow_permission_macros,

	# Rename typeattribute to attribute to match written sepolicy
	Macro(
		'attribute',
		[
			Match(['typeattribute', '$1']),
		],
		replace_named_macro,
	),

	Macro(
		'replace base_typeattr_ typeattributeset',
		[
			Match(['typeattributeset', 'base_typeattr_$1']),
		],
		replace_typeattributeset_base_typeattr,
	),

	Macro(
		'split typeattributeset',
		[
			Match(['typeattributeset']),
		],
		replace_typeattributeset,
	),

	Macro(
		'domain_trans',
		[
			Match(['allow', '$1', '$2', 'file'], equal=['getattr', 'open', 'read', 'execute', 'map']),
			Match(['allow', '$1', '$3', 'process'], equal=['transition']),
			Match(['allow', '$3', '$2', 'file'], equal=['entrypoint', 'open', 'read', 'execute', 'getattr', 'map']),
			Match(['dontaudit', '$1', '$3', 'process'], equal=['noatsecure']),
			Match(['allow', '$1', '$3', 'process'], equal=['siginh', 'rlimitinh']),
		],
		replace_named_macro,
	),
	Macro(
		'domain_auto_trans',
		[
			Match(['domain_trans', '$1', '$2', '$3']),
			Match(['typetransition', '$1', '$2', 'process', '$3']),
		],
		replace_named_macro,
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
		replace_named_macro,
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
		replace_named_macro,
	),
	Macro(
		'init_daemon_domain',
		[
			Match(['domain_auto_trans', 'init', '$1_exec', '$1']),
		],
		replace_named_macro,
	),
	Macro(
		'r_dir_file',
		[
			Match(['allow', '$1', '$2', 'dir'], equal=['r_dir_perms']),
			Match(['allow', '$1', '$2', 'file'], equal=['r_file_perms']),
			Match(['allow', '$1', '$2', 'lnk_file'], equal=['r_file_perms']),
		],
		replace_named_macro,
	),
	Macro(
		'unix_socket_connect',
		[
			Match(['allow', '$1', '$2_socket', 'sock_file'], equal=['write']),
			Match(['allow', '$1', '$3', 'unix_stream_socket'], equal=['connectto']),
		],
		replace_named_macro,
	),
	Macro(
		'unix_socket_send',
		[
			Match(['allow', '$1', '$2_socket', 'sock_file'], equal=['write']),
			Match(['allow', '$1', '$3', 'unix_dgram_socket'], equal=['sendto']),
		],
		replace_named_macro,
	),
	Macro(
		'get_prop',
		[
			Match(['allow', '$1', '$2', 'file'], equal=['getattr', 'open', 'read', 'map']),
		],
		replace_named_macro,
	),
	Macro(
		'set_prop',
		[
			Match(['allow', '$1', '$2', 'property_service'], equal=['set']),
			Match(['unix_socket_connect', '$1', 'property', 'init']),
			Match(['get_prop', '$1', '$2']),
		],
		replace_named_macro,
	),
	Macro(
		'binder_service',
		[
			Match(['typeattribute', '$1', 'binderservicedomain']),
		],
		replace_named_macro,
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
		replace_named_macro,
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
		replace_named_macro,
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
		replace_named_macro,
	),
	Macro(
		'binder_call',
		[
			Match(['allow', '$1', '$2', 'binder'], equal=['call', 'transfer']),
			Match(['allow', '$2', '$1', 'binder'], equal=['transfer']),
			Match(['allow', '$1', '$2', 'fd'], equal=['use']),
		],
		replace_named_macro,
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
		replace_named_macro,
	),
	Macro(
		'userfaultfd_use',
		[
			Match(['typetransition', '$1', '$1', 'anon_inode', '"[userfaultfd]"', '$1_userfaultfd']),
			Match(['allow', '$1', '$1_userfaultfd', 'anon_inode'], equal=['create', 'ioctl', 'read']),
			Match(['neverallow', '{ domain -$1 }', '$1_userfaultfd', 'anon_inode'], equal=['*']),
			Match(['neverallow', '$1', '~$1_userfaultfd', 'anon_inode'], equal=['*']),
		],
		replace_named_macro,
	),
	Macro(
		'app_domain',
		[
			Match(['typeattribute', '$1', 'appdomain']),
			Match(['typetransition', '$1', 'tmpfs', 'file', 'appdomain_tmpfs']),
			Match(['userfaultfd_use', '$1'], optional=True),
			Match(['allow', '$1', 'appdomain_tmpfs', 'file'],
			      equal=['execute', 'getattr', 'map', 'read', 'write']),
			Match(['neverallow', '{ $1 -runas_app -shell -simpleperf }', '{ domain -$1 }', 'file'],
			      equal=['no_rw_file_perms']),
			Match(['neverallow', '{ appdomain -runas_app -shell -simpleperf -$1 }', '$1', 'file'],
			      equal=['no_rw_file_perms']),
			Match(['neverallow', '{ domain -crash_dump -runas_app -simpleperf -$1 }', '$1', 'process'],
			      equal=['ptrace'], optional=True),
			Match(['neverallow', '{ domain -crash_dump -llkd -runas_app -simpleperf -$1 }', '$1', 'process'],
			      equal=['ptrace'], optional=True),
		],
		replace_named_macro,
		lambda rules: (rules[6] is not None) ^ (rules[7] is not None),
	),
	Macro(
		'net_domain',
		[
			Match(['typeattribute', '$1', 'netdomain']),
		],
		replace_named_macro,
	),
	Macro(
		'hal_attribute',
		[
			Match(['attribute', 'hal_$1']),
			Match(['attribute', 'hal_$1_client']),
			Match(['attribute', 'hal_$1_server']),
		],
		replace_named_macro,
	),
	Macro(
		'hal_server_domain',
		[
			Match(['typeattribute', '$1', '$2_server']),
			Match(['typeattribute', '$1', '$2']),
			Match(['typeattribute', '$1', 'halserverdomain']),
		],
		replace_named_macro,
	),
	Macro(
		'passthrough_hal_client_domain',
		[
			Match(['typeattribute', '$1', 'halclientdomain']),
			Match(['typeattribute', '$1', '$2_client']),
			Match(['typeattribute', '$1', '$2']),
		],
		replace_named_macro,
	),
	Macro(
		'hal_client_domain',
		[
			Match(['typeattribute', '$1', 'halclientdomain']),
			Match(['typeattribute', '$1', '$2_client']),
		],
		replace_named_macro,
	),
	Macro(
		'add_service',
		[
			Match(['allow', '$1', '$2', 'service_manager'], equal=['add', 'find']),
			Match(['neverallow', '{ domain -$1 }', '$2', 'service_manager'], equal=['add']),
		],
		replace_named_macro,
	),
	Macro(
		'add_hwservice',
		[
			Match(['allow', '$1', '$2', 'hwservice_manager'], equal=['add', 'find']),
			Match(['allow', '$1', 'hidl_base_hwservice', 'hwservice_manager'], equal=['add']),
			Match(['neverallow', '{ domain -$1 }', '$2', 'hwservice_manager'], equal=['add']),
		],
		replace_named_macro,
	),
	Macro(
		'hal_attribute_service',
		[
			Match(['allow', '$1_client', '$2', 'service_manager'], equal=['find']),
			Match(['add_service', '$1_server', '$2']),
		],
		replace_named_macro,
	),
	Macro(
		'hal_attribute_hwservice',
		[
			Match(['allow', '$1_client', '$2', 'hwservice_manager'], equal=['find']),
			Match(['add_hwservice', '$1_server', '$2']),
			Match(['neverallow', '{ domain -$1_client -$1_server }', '$2', 'hwservice_manager'], equal=['find']),
		],
		replace_named_macro,
	),

	# Form a type statement from leftover typeattributes
	Macro(
		'type',
		[
			Match(['typeattribute', '$1', '$2']),
		],
		replace_typeattribute_with_type,
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
		replace_named_macro,
	),
]


def extend_matched_types(macro, matched_types):
	for i in range(len(matched_types), macro.max_index + 1):
		matched_types.append(None)


def merge_matched_types(old_matched_types, new_matched_types):
	merged_matched_types = old_matched_types[:]

	for i in range(len(new_matched_types)):
		if old_matched_types[i] is None and \
				new_matched_types[i] is not None:
			merged_matched_types[i] = new_matched_types[i]
		elif old_matched_types[i] is not None and \
				new_matched_types[i] is not None:
			return None

	return merged_matched_types


def match_macro_rules(mld, match_results, macro, index, rules, matched_types):
	extend_matched_types(macro, matched_types)

	if index == len(macro.matches):
		if macro.is_fully_filled and \
			(macro.check_fn is None or macro.check_fn(rules)):
			match_result = MacroMatchResult(macro, rules, matched_types)
			match_results.append(match_result)

		return

	match = macro.matches[index]
	matched_rules = mld.get(match)

	def call_again(new_rule, new_macro, merged_matched_types):
		new_rules = rules[:] + [new_rule]

		match_macro_rules(mld, match_results, new_macro, index + 1,
				  new_rules, merged_matched_types)

	if not len(matched_rules) and match.optional:
		merged_matched_types = matched_types[:]
		new_macro = macro

		call_again(None, new_macro, merged_matched_types)

	for rule in matched_rules:
		new_matched_types = match.extract_matched_indices(rule)
		merged_matched_types = merge_matched_types(matched_types, new_matched_types)
		if merged_matched_types is None:
			continue

		new_macro = macro.fill_matched_indices(new_matched_types)

		call_again(rule, new_macro, merged_matched_types)


def match_and_replace_macro(mld, macro):
	match_results = []

	match_macro_rules(mld, match_results, macro, 0, [], [])

	replace_results = []

	for match_result in match_results:
		replace_result = macro.replace_fn(mld, match_result)
		if replace_result is None:
			continue

		replace_results.append(replace_result)

	for replace_result in replace_results:
		for rule in replace_result.removed:
			mld.remove(rule)

	for replace_result in replace_results:
		for rule in replace_result.added:
			mld.add(rule)


def match_and_replace_macros(mld):
	for macro in macros:
		print(f'Processing macro {macro.name}...')
		match_and_replace_macro(mld, macro)


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
node_perms = ['recvfrom', 'sendto']
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
# compiled rule also contains entrypoint and execute_no_trans
# chr_file_perms = common_file_perms
chr_file_perms = file_perms

common_socket_perms = ['accept', 'append', 'bind', 'connect', 'create', 'getattr', 'getopt', 'ioctl', 'listen', 'lock',
		       'map', 'name_bind', 'read', 'recvfrom', 'relabelfrom', 'relabelto', 'sendto', 'setattr', 'setopt',
		       'shutdown', 'write']
tcp_socket_perms = common_socket_perms + ['name_connect', 'node_bind']
icmp_socket_perms = common_socket_perms + ['node_bind']
sctp_socket_perms = tcp_socket_perms + ['association']
unix_stream_socket_perms = common_socket_perms + ['connectto']
tun_socket_perms = common_socket_perms + ['attach_queue']
netlink_xfrm_socket_perms = common_socket_perms + ['nlmsg_read', 'nlmsg_write']
# compiled rule contains nlmsg_readpriv too
# netlink_route_socket_perms = netlink_xfrm_socket_perms
netlink_route_socket_perms = netlink_xfrm_socket_perms + ['nlmsg_readpriv']
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

# netbroadcast is actually net_broadcast
# audit_control is added in compiled rule
# capability_perms = ['audit_write', 'chown', 'dac_override', 'dac_read_search', 'fowner', 'fsetid', 'ipc_lock', 'ipc_owner',
# 		    'kill', 'lease', 'linux_immutable', 'mknod', 'net_admin', 'net_bind_service', 'net_raw', 'netbroadcast',
# 		    'setfcap', 'setgid', 'setpcap', 'setuid', 'sys_admin', 'sys_boot', 'sys_chroot', 'sys_module', 'sys_nice',
# 		    'sys_pacct', 'sys_ptrace', 'sys_rawio', 'sys_resource', 'sys_time', 'sys_tty_config']
capability_perms = ['audit_write', 'chown', 'dac_override', 'dac_read_search', 'fowner', 'fsetid', 'ipc_lock', 'ipc_owner',
		    'kill', 'lease', 'linux_immutable', 'mknod', 'net_admin', 'net_bind_service', 'net_raw', 'net_broadcast',
		    'setfcap', 'setgid', 'setpcap', 'setuid', 'sys_admin', 'sys_boot', 'sys_chroot', 'sys_module', 'sys_nice',
		    'sys_pacct', 'sys_ptrace', 'sys_rawio', 'sys_resource', 'sys_time', 'sys_tty_config', 'audit_control']

# bpf missing from compiled rule
# capability2_perms = ['audit_read', 'bpf', 'block_suspend', 'mac_admin', 'mac_override', 'perfmon', 'syslog', 'wake_alarm']
capability2_perms = ['audit_read', 'block_suspend', 'mac_admin', 'mac_override', 'perfmon', 'syslog', 'wake_alarm']

security_perms = ['check_context', 'compute_av', 'compute_create', 'compute_member', 'compute_relabel', 'compute_user',
		  'load_policy', 'read_policy', 'setbool', 'setcheckreqprot', 'setenforce', 'setsecparam', 'validate_trans']

system_perms = ['ipc_info', 'module_load', 'module_request', 'syslog_console', 'syslog_mod', 'syslog_read']
binder_perms = ['call', 'impersonate', 'set_context_mgr', 'transfer']
key_perms = ['create', 'link', 'read', 'search', 'setattr', 'view', 'write']

property_service_perms = ['set']
service_manager_perms = ['add', 'find', 'list']
keystore_key_perms = ['get_state', 'get', 'insert', 'delete', 'exist', 'list', 'reset', 'password', 'lock', 'unlock',
		      'is_empty', 'sign', 'verify', 'grant', 'duplicate', 'clear_uid', 'add_auth', 'user_changed',
		      'gen_unique_id']
drmservice_perms = ['consumeRights', 'setPlaybackStatus', 'openDecryptSession', 'closeDecryptSession',
		    'initializeDecryptUnit', 'decrypt', 'finalizeDecryptUnit', 'pread']

all_perms_types = {
	'fd': fd_perms,
	'peer': peer_perms,
	'memprotect': memprotect_perms,
	'netif': netif_perms,
	'node': node_perms,
	'packet': packet_perms,
	'association': association_perms,
	'bpf': bpf_perms,
	'perf_event': perf_event_perms,
	'filesystem': filesystem_perms,

	'lnk_file': common_file_perms,
	'blk_file': common_file_perms,
	'sock_file': common_file_perms,
	'fifo_file': common_file_perms,
	'anon_inode': common_file_perms,
	'chr_file': chr_file_perms,
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
	'dccp_socket': tcp_socket_perms,
	'unix_stream_socket': unix_stream_socket_perms,
	'tun_socket': tun_socket_perms,
	'netlink_xfrm_socket': netlink_xfrm_socket_perms,
	'netlink_firewall_socket': netlink_xfrm_socket_perms,
	'netlink_tcpdiag_socket': netlink_xfrm_socket_perms,
	'netlink_ip6fw_socket': netlink_xfrm_socket_perms,
	'netlink_route_socket': netlink_route_socket_perms,
	'netlink_audit_socket': netlink_audit_socket_perms,
	'sctp_socket': sctp_socket_perms,
	'icmp_socket': icmp_socket_perms,
	'udp_socket': icmp_socket_perms,
	'rawip_socket': icmp_socket_perms,

	'ipc': ipc_perms,
	'sem': ipc_perms,
	'msgq': msgq_perms,
	'msg': msg_perms,
	'shm': shm_perms,

	'process': process_perms,
	'process2': process2_perms,
	'capability': capability_perms,
	'capability2': capability2_perms,
	'cap_userns': capability_perms,
	'cap2_userns': capability2_perms,

	'security': security_perms,
	'system': system_perms,
	'binder': binder_perms,
	'key': key_perms,

	'property_service': property_service_perms,
	'service_manager': service_manager_perms,
	'hwservice_manager': service_manager_perms,
	'keystore_key': keystore_key_perms,
	'drmservice': drmservice_perms,
}

neverallow_permission_macro_names = [
	'no_w_dir_perms',
	'no_x_file_perms',
	'no_rw_file_perms',
	'no_w_file_perms',
]

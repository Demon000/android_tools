#!/usr/bin/env python3

import sys
import fdt

if len(sys.argv) < 3:
    sys.exit(1)

dts_file = sys.argv[1]
out_dts_file = sys.argv[2]

with open(dts_file, 'r') as f:
    dts_text = f.read()

dt = fdt.parse_dts(dts_text)

def for_each_node(node, fn, max_recurse_level=-1, recurse_level=0):
    if max_recurse_level != -1 and recurse_level > max_recurse_level:
        return

    fn(node)

    for child_node in node.nodes:
        for_each_node(child_node, fn, max_recurse_level, recurse_level + 1)

def split_node_name(name):
    addr_del = '@'
    if addr_del in name:
        parts = name.split(addr_del)
        name = parts[0]
        addr = int(parts[1], 16)
        return (name, addr)

    return (name, 0)

def sort_props(prop):
    return str(prop)

def sort_nodes(node):
    return split_node_name(node.name)

def sort_node(node):
    node._props.sort(key=sort_props)
    node._nodes.sort(key=sort_nodes)

for_each_node(dt.root, sort_node)

def print_node_phandle(node):
    if node.exist_property('phandle'):
        phandle_prop = node.get_property('phandle')
        print(node.path, node.name, hex(phandle_prop.value))
    node.remove_property('phandle')

for_each_node(dt.root, print_node_phandle)

with open(out_dts_file, 'w') as f:
    f.write(dt.to_dts())

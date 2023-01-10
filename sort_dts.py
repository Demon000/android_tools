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

def for_each_node(node, fn):
    fn(node)

    for child_node in node.nodes:
        for_each_node(child_node, fn)

def sort_props(prop):
    return str(prop)

def sort_nodes(node):
    addr_del = '@'
    if addr_del in node.name:
        parts = node.name.split(addr_del)
        name = parts[0]
        addr = int(parts[1], 16)
        return (name, addr)

    return (node.name, 0)

def sort_node(node):
    node._props.sort(key=sort_props)
    node._nodes.sort(key=sort_nodes)

for_each_node(dt.root, sort_node)


with open(out_dts_file, 'w') as f:
    f.write(dt.to_dts())

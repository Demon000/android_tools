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

def sort_props(prop):
    return str(prop)

def sort_nodes(node):
    return node.name

def recurse_node(node):
    node._props.sort(key=sort_props)
    node._nodes.sort(key=sort_nodes)

    for child_node in node.nodes:
        recurse_node(child_node)

recurse_node(dt.root)

with open(out_dts_file, 'w') as f:
    f.write(dt.to_dts())

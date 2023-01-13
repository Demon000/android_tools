#!/usr/bin/env python3

import re
import sys
import fdt

def for_each_node(node, fn, *args, max_recurse_level=-1, recurse_level=0, **kwargs):
    if node is None:
        return

    if max_recurse_level != -1 and recurse_level > max_recurse_level:
        return

    fn(node, *args, **kwargs)

    for child_node in node.nodes:
        for_each_node(
            child_node, fn, *args,
            max_recurse_level=max_recurse_level,
            recurse_level=recurse_level + 1,
            **kwargs)

def split_node_name(name):
    addr_del = '@'
    if addr_del in name:
        parts = name.split(addr_del)
        name = parts[0]
        addr = int(parts[1], 16)
        return (name, addr)

    return (name, 0)

FRAGMENT_NAME = 'fragment'

def gen_fragment_name(index):
    return f'{FRAGMENT_NAME}@{index:x}'

def is_fragment_name(name):
    return name == FRAGMENT_NAME

def reindex_fragment(node, fragment_ctx):
    fragment_mapping = fragment_ctx['mapping']

    name, index = split_node_name(node.name)
    if not is_fragment_name(name):
        return

    if index not in fragment_mapping:
        fragment_mapping[index] = fragment_ctx['index']
        fragment_ctx['index'] += 1

    replacement_index = fragment_mapping[index]

    node.set_name(gen_fragment_name(replacement_index))

def reindex_fixup(prop, fragment_mapping):
    for i, data in enumerate(prop.data):
        parts = data.split('\\0')

        for j, part in enumerate(parts):
            path_parts = re.split(r'/|:', part)

            for k, path_part in enumerate(path_parts):
                name, index = split_node_name(path_part)
                if not is_fragment_name(name):
                    continue

                path_parts[k] = gen_fragment_name(fragment_mapping[index])

            parts[j] = '/'.join(path_parts)

        prop.data[i] = '\\0'.join(parts)

def reindex_fixups(node, fragment_ctx):
    fragment_mapping = fragment_ctx['mapping']
    for prop in node.props:
        reindex_fixup(prop, fragment_mapping)

def dt_reindex_fragments(dt):
    fragment_ctx = {
        'index': 0,
        'mapping': {},
    }
    local_fixups_node = dt.root.get_subnode('__local_fixups__')
    fixups_node = dt.root.get_subnode('__fixups__')
    symbols_node = dt.root.get_subnode('__symbols__')

    for_each_node(
        dt.root,
        reindex_fragment,
        fragment_ctx,
        max_recurse_level=1)
    for_each_node(
        local_fixups_node,
        reindex_fragment,
        fragment_ctx,
        max_recurse_level=1)
    for_each_node(fixups_node,
        reindex_fixups,
        fragment_ctx,
        max_recurse_level=1)
    for_each_node(symbols_node,
        reindex_fixups,
        fragment_ctx,
        max_recurse_level=1)

def sort_props(prop):
    return str(prop)

def sort_nodes(node):
    return split_node_name(node.name)

def sort_node(node):
    node._props.sort(key=sort_props)
    node._nodes.sort(key=sort_nodes)

def dt_sort_nodes(dt):
    for_each_node(dt.root, sort_node)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)

    dts_file = sys.argv[1]
    out_dts_file = sys.argv[2]

    if dts_file.endswith('.dts'):
        with open(dts_file, 'r') as f:
            dts_text = f.read()

        dt = fdt.parse_dts(dts_text)
    elif dts_file.endswith('.dtb'):
        with open(dts_file, 'rb') as f:
            dtb_bin = f.read()

        dt = fdt.parse_dtb(dtb_bin)

    dt_reindex_fragments(dt)
    dt_sort_nodes(dt)

    with open(out_dts_file, 'w') as f:
        f.write(dt.to_dts())

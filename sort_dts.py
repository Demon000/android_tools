#!/usr/bin/env python3

import re
import sys
import fdt
from fdt_extra import *

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

def replace_phandle_with_label(path, name, addr, label=None, phandle_labels_map=None):
    index = addr // 4
    node = dt.get_node(path)
    ref_prop = node.get_property(name)

    if type(ref_prop) == fdt.PropWords:
        new_prop = PropWordsWithPhandles(name, *ref_prop.data)
        node.remove_property(name)
        node.append(new_prop)
    elif type(ref_prop) == PropWordsWithPhandles:
        new_prop = ref_prop
    else:
        raise ValueError()

    if not label:
        phandle = new_prop.data[index]
        label = phandle_labels_map[phandle][0]

    new_prop.set_phandle_name(index, label)

def dt_fill_fixups(dt):
    fixups_node = dt.root.get_subnode('__fixups__')
    if fixups_node is None:
        return

    fixups_props = {}

    for prop in fixups_node.props:
        for value in prop.data:
            value_parts = value.split(':')
            node_path = value_parts[0]
            prop_name = value_parts[1]
            prop_data_index = int(value_parts[2])

            replace_phandle_with_label(node_path, prop_name, prop_data_index,
                prop.name)

    dt.root.remove_subnode('__fixups__')

def dt_fill_symbols(dt):
    SYMBOLS = '__symbols__'
    LOCAL_FIXUPS = '__local_fixups__'

    local_fixups_node = dt.root.get_subnode(LOCAL_FIXUPS)
    symbols_node = dt.root.get_subnode(SYMBOLS)
    phandle_labels_map = {}

    if local_fixups_node is None or symbols_node is None:
        return

    for prop in symbols_node.props:
        assert type(prop) == fdt.PropStrings

        label = prop.name
        path = prop.value
        node = dt.get_node(path)
        phandle = node.get_property('phandle').value

        if phandle not in phandle_labels_map:
            phandle_labels_map[phandle] = []

        phandle_labels_map[phandle].append(label)

        if node.label:
            label = f'{node.label}: {label}'

        node.set_label(label)

    def replace_phandles_with_label(node):
        for prop in node.props:
            abs_node_path = prop.path.removeprefix(f'/{LOCAL_FIXUPS}')

            for value in prop.data:
                replace_phandle_with_label(abs_node_path, prop.name, value,
                    phandle_labels_map=phandle_labels_map)

    for_each_node(local_fixups_node, replace_phandles_with_label)

    dt.root.remove_subnode(LOCAL_FIXUPS)
    dt.root.remove_subnode(SYMBOLS)

def sort_props(prop):
    return str(prop)

def sort_nodes(node):
    return node.name

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

    if dts_file.endswith('.dts') or dts_file.endswith('.dtsi'):
        with open(dts_file, 'r') as f:
            dts_text = f.read()

        dt = fdt.parse_dts(dts_text)
    elif dts_file.endswith('.dtb') or dts_file.endswith('.dtbo'):
        with open(dts_file, 'rb') as f:
            dtb_bin = f.read()

        dt = fdt.parse_dtb(dtb_bin)
    else:
        raise ValueError(f'Invalid file extension')

    dt_fill_fixups(dt)
    dt_fill_symbols(dt)
    dt_sort_nodes(dt)

    with open(out_dts_file, 'w') as f:
        f.write(dt.to_dts())

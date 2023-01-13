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
            node_path, prop_name, prop_data_index = value.split(':')
            prop_data_index = int(prop_data_index)

            replace_phandle_with_label(node_path, prop_name, prop_data_index,
                prop.name)

    dt.root.remove_subnode('__fixups__')

def dt_fill_symbols(dt):
    SYMBOLS = '__symbols__'
    symbols_node = dt.root.get_subnode(SYMBOLS)
    phandle_labels_map = {}

    if symbols_node is None:
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

    dt.root.remove_subnode(SYMBOLS)

    LOCAL_FIXUPS = '__local_fixups__'
    local_fixups_node = dt.root.get_subnode(LOCAL_FIXUPS)

    if local_fixups_node is None:
        return

    def replace_phandles_with_label(node):
        for prop in node.props:
            abs_node_path = prop.path.removeprefix(f'/{LOCAL_FIXUPS}')

            for value in prop.data:
                replace_phandle_with_label(abs_node_path, prop.name, value,
                    phandle_labels_map=phandle_labels_map)

    for_each_node(local_fixups_node, replace_phandles_with_label)

    dt.root.remove_subnode(LOCAL_FIXUPS)

def sort_props(prop):
    return str(prop)

def sort_nodes(node):
    return node.name

def sort_node(node):
    node._props.sort(key=sort_props)
    node._nodes.sort(key=sort_nodes)

def dt_sort_nodes(dt):
    for_each_node(dt.root, sort_node)

def node_is_fragment(node):
    return node.name.startswith('fragment@')

def dt_extract_overlays(dt):
    overlay_nodes = {}

    for node in dt.root.nodes:
        if not node_is_fragment(node):
            continue

        overlay_target = node.get_property('target')
        assert type(overlay_target) == PropWordsWithPhandles
        overlay_label = overlay_target.get_phandle_name(0)

        if overlay_label not in overlay_nodes:
            overlay_nodes[overlay_label] = []

        overlay_node = node.get_subnode('__overlay__')
        overlay_node.set_name(f'&{overlay_label}')

        overlay_nodes[overlay_label].append(overlay_node)
        names = [node.name for node in overlay_nodes[overlay_label]]

    dt.root._nodes = [node for node in dt.root._nodes if not node_is_fragment(node)]

    merged_overlays = []

    for label in overlay_nodes:
        overlays = overlay_nodes[label]
        first_overlay = overlays[0]

        for overlay in overlays[1:]:
            first_overlay.merge(overlay, replace=True)

        sort_node(first_overlay)

        merged_overlays.append(first_overlay)

    merged_overlays.sort(key=sort_nodes)

    return merged_overlays

def remove_phandle(node):
    node.remove_property('phandle')

def dt_remove_phandles(dt):
    for_each_node(dt.root, remove_phandle)

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
    dt_remove_phandles(dt)
    dt_sort_nodes(dt)
    overlays = dt_extract_overlays(dt)

    with open(out_dts_file, 'w') as f:
        f.write(dt.to_dts())

        if overlays:
            f.write('\n')
            for overlay in overlays:
                f.write(overlay.to_dts())
                f.write('\n')

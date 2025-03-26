#!/usr/bin/env python

import argparse
from parser import create_builtins

from utils import import_module

args_parser = argparse.ArgumentParser("Parse bazel scripts")
args_parser.add_argument("script", help="Script to parse")
args_parser.add_argument("--root", action="store", help="Root of android tree")
args_parser.add_argument("--debug", action="store_true", help="Debug")
args_parser.add_argument("--module", action="append", help="Maps from one path to another")
args = args_parser.parse_args()

module_map = {}
for module in args.module:
    src_module_path, dst_module_path = module.split(':')
    module_map[src_module_path] = dst_module_path

create_builtins(args.root, module_map, args.debug)

import_module(args.script)

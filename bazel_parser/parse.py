#!/usr/bin/env python

import argparse
from kbuild_writer import write_kbuild
from parser_impl import BazelParser

args_parser = argparse.ArgumentParser("Parse bazel scripts")
args_parser.add_argument("script", help="Script to parse")
args_parser.add_argument("kbuild", help="Kbuild to output")
args_parser.add_argument(
    "-r",
    "--root",
    action="store",
    help="Root of android tree",
)
args_parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    help="Debug",
)
args_parser.add_argument(
    "-b",
    "--print-bazel-output",
    action="store_true",
    help="Print output of bazel scripts",
)
args_parser.add_argument(
    "-m",
    "--module-path",
    action="append",
    help="Maps from one path to another",
)
args_parser.add_argument(
    "-f",
    "--flag",
    action="append",
    help="Set flag",
)
args = args_parser.parse_args()

module_paths_map = {}
if args.module_path:
    for module_path in args.module_path:
        src_module_path, dst_module_path = module_path.split(":")
        module_paths_map[src_module_path] = dst_module_path

flags_map = {}
if args.flag:
    for flag in args.flag:
        flag_key, flag_value = flag.split(':')
        flags_map[flag_key] = flag_value


bazel_parser = BazelParser(
    android_root=args.root,
    module_paths_map=module_paths_map,
    flags_map=flags_map,
    debug=args.debug,
    print_bazel_output=args.print_bazel_output,
)

bazel_parser.parse(args.script)

write_kbuild(args.kbuild, bazel_parser)

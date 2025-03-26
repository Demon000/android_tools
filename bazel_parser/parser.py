import builtins
from os import path
from pprint import pprint
from typing import List
from utils import import_module
from types import SimpleNamespace
from glob import glob

ABS_MODULE_START = "//"


class depset_impl(set):
    def to_list(self):
        return list(self)


def create_builtins(
    android_root: str,
    module_map: dict[str, str],
    debug: bool,
):
    def struct(**kwargs):
        if debug:
            print("struct", kwargs)
        s = SimpleNamespace()
        for k, v in kwargs.items():
            setattr(s, k, v)
        return s

    def package(*args, **kwargs):
        if debug:
            print("package", args, kwargs)

    def load(module_path: str, *names: List[str]):
        if debug:
            print("load", module_path, names)
        module_root, file_path = module_path.split(":", 1)

        if module_root:
            assert module_root.startswith(ABS_MODULE_START)
            module_root = module_root[len(ABS_MODULE_START) :]

            if module_root not in module_map:
                if debug:
                    print(f"Ignore module root: {module_root}")
                return

            file_path = path.join(android_root, module_map[module_root], file_path)

        module = import_module(file_path)

        for name in names:
            value = getattr(module, name)
            setattr(builtins, name, value)

    def ddk_headers(*args, **kwargs):
        if debug:
            print("ddk_headers", args, kwargs)

    def ddk_submodule(**data):
        if debug:
            print("ddk_submodule")
            pprint(data)
            print()

    def ddk_module(**data):
        if debug:
            print("ddk_module")
            pprint(data)
            print()

    def copy_to_dist_dir(**data):
        if debug:
            print("copy_to_dist_dir")
            pprint(data)
            print()

    def glob_impl(globs: List[str]):
        if debug:
            print("glob", globs)

        found_files = []
        for g in globs:
            g_files = glob(g, recursive=True)
            found_files.extend(g_files)

        return found_files

    def depset(*args, **kwargs):
        if debug:
            print("depset", args, kwargs)

        return depset_impl(*args, **kwargs)

    def native_genrule(*args, **kwargs):
        if debug:
            print("native_genrule", args, kwargs)

    def native_glob(
        include=None,
        exclude=None,
        exclude_directories=True,
        allow_empty=True,
    ):
        if include is None:
            include = []

        if exclude is None:
            exclude = []

        if debug:
            print("native_glob", include, exclude, exclude_directories, allow_empty)

        found_files = set()
        for g in include:
            g_files = glob(g, recursive=True)
            print(g, g_files)
            if not g_files and not allow_empty:
                assert False
            found_files.update(g_files)

        excluded_files = set()
        for g in exclude:
            g_files = glob(g, recursive=True)
            excluded_files.update(g_files)

        if not found_files and not allow_empty:
            assert False

        found_directories = set()
        if exclude_directories:
            for found_file in found_files:
                if path.isdir(found_file):
                    found_directories.add(found_file)

        return list(found_files - excluded_files - found_directories)

    builtins.native = SimpleNamespace()
    setattr(builtins.native, "genrule", native_genrule)
    setattr(builtins.native, "glob", native_glob)

    builtins.depset = depset
    builtins.struct = struct
    builtins.package = package
    builtins.load = load
    builtins.ddk_headers = ddk_headers
    builtins.ddk_submodule = ddk_submodule
    builtins.ddk_module = ddk_module
    builtins.copy_to_dist_dir = copy_to_dist_dir
    builtins.glob = glob_impl

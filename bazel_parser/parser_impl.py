import builtins
import re
from glob import glob
from io import TextIOWrapper
from os import path
from types import SimpleNamespace
from typing import Dict, List, Optional, Set, TypeVar

from consts import X86_64_OUTS, aarch64_outs
from rules import (
    Alias,
    BoolFlag,
    ConfigSetting,
    DdkHeaders,
    DdkModule,
    DdkSubModule,
    GenRule,
    Rule,
)

from utils import TemporaryWorkingDirectory, import_module

IMPL_MODULE_START = "@"
ABS_MODULE_START = "//"
BUILD_BAZEL_FILE_NAME = "BUILD.bazel"


class depset_impl(set):
    def to_list(self):
        return list(self)


def native_glob_impl(
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    exclude_directories: Optional[bool] = True,
    allow_empty: Optional[bool] = True,
):
    if include is None:
        include = []

    if exclude is None:
        exclude = []

    found_files = set()
    for g in include:
        g_files = glob(g, recursive=True)
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

    files = list(found_files - excluded_files - found_directories)
    files.sort()

    return files


T = TypeVar("T", bound=Rule)


class BazelParser:
    failed_imports: Set[str] = set()
    mapped_imports: Set[str] = set()

    def __init__(
        self,
        android_root: Optional[str],
        module_paths_map: Dict[str, str],
        flags_map: Dict[str, str],
        debug: Optional[bool],
        print_bazel_output: Optional[bool],
    ):
        self.android_root = android_root
        self.module_paths_map = module_paths_map
        self.flags_map = flags_map
        self.debug = debug
        self.print_bazel_output = print_bazel_output
        self.targets: Dict[str, Rule] = {}
        self.original_print = builtins.print

        self.overriden_rules = {
            "attr": SimpleNamespace(
                {
                    "label": self.dummy("attr.label"),
                    "int": self.dummy("attr.int"),
                    "string_list": self.dummy("attr.string_list"),
                }
            ),
            "hermetic_toolchain": SimpleNamespace(
                {
                    "type": self.dummy("hermetic_toolchain.type"),
                }
            ),
            "native": SimpleNamespace(
                {
                    "alias": self.add_target_impl(Alias),
                    "genrule": self.add_target_impl(GenRule),
                    "glob": self.native_glob_wrapper,
                    "config_setting": self.dummy("native.config_setting"),
                    "filegroup": self.dummy("native.filegroup"),
                }
            ),
            "checkpatch": self.dummy("checkpatch"),
            "write_file": self.dummy("write_file"),
            "filegroup": self.dummy("filegroup"),
            "rule": self.rule_impl(),
            "define_common_kernels": self.dummy("define_common_kernels"),
            "kernel_abi": self.dummy("kernel_abi"),
            "kernel_abi_dist": self.dummy("kernel_abi_dist"),
            "kernel_build": self.dummy("kernel_build"),
            "kernel_build_config": self.dummy("kernel_build_config"),
            "kernel_modules_install": self.dummy("kernel_modules_install"),
            "kernel_images": self.dummy("kernel_images"),
            "merged_kernel_uapi_headers": self.dummy("merged_kernel_uapi_headers"),
            "kernel_uapi_headers_cc_library": self.dummy(
                "kernel_uapi_headers_cc_library"
            ),
            "kernel_compile_commands": self.dummy("kernel_compile_commands"),
            "copy_to_dist_dir": self.dummy("copy_to_dist_dir"),
            "super_image": self.dummy("super_image"),
            "unsparsed_image": self.dummy("unsparsed_image"),
            "hermetic_genrule": self.dummy("hermetic_genrule"),
            "X86_64_OUTS": X86_64_OUTS,
            "aarch64_outs": aarch64_outs,
            "bool_flag": self.add_target_impl(BoolFlag),
            "config_setting": self.add_target_impl(ConfigSetting),
            "alias": self.add_target_impl(Alias),
            "genrule": self.add_target_impl(GenRule),
            "ddk_headers": self.add_target_impl(DdkHeaders),
            "ddk_submodule": self.add_target_impl(DdkSubModule),
            "ddk_module": self.add_target_impl(DdkModule),
            "depset": self.depset_wrapper,
            "select": self.select_impl,
            "struct": self.struct_impl,
            "package": self.package_impl,
            "load": self.load_impl,
            "glob": self.glob_impl,
            "fail": self.fail_impl,
        }

        if not self.print_bazel_output:
            self.overriden_rules["print"] = self.print_impl

    def map_module_to_path(self, module_name: str):
        if module_name.startswith(IMPL_MODULE_START):
            return None

        assert module_name.startswith(ABS_MODULE_START)
        module_name = module_name[len(ABS_MODULE_START) :]

        mapped_module_path = None
        for module_name_repl, module_path in self.module_paths_map.items():
            if module_name == module_name_repl:
                mapped_module_path = module_path
                break

            module_name_repl_dir = f"{module_name_repl}/"
            if module_name.startswith(module_name_repl_dir):
                trimmed_module_name = module_name[len(module_name_repl_dir) :]
                mapped_module_path = path.join(module_path, trimmed_module_name)
                break

        if mapped_module_path is not None:
            if mapped_module_path not in self.mapped_imports:
                self.original_print(f"Mapped {module_name} to {mapped_module_path}")
                self.mapped_imports.add(module_name)

            module_name = mapped_module_path

        if module_name.startswith(ABS_MODULE_START):
            assert self.android_root is not None
            module_name = path.join(self.android_root, module_name)

        return module_name

    def spec_resolution(self, spec: str, target_is_file=False):
        # There are multiple spec types
        # target
        # :file.bzl
        # :target
        # //path/to/module/root:file.bzl
        # //path/to/module/root:target

        if ":" not in spec:
            return None, None

        module_name, target_name = spec.split(":", 1)
        if not module_name and target_is_file:
            return "", target_name

        module_path = self.map_module_to_path(module_name)
        if not module_path:
            return None, None

        if target_is_file:
            module_path = path.join(module_path, target_name)
        else:
            module_path = path.join(module_path, BUILD_BAZEL_FILE_NAME)

        return module_name, module_path

    def parse_module(self, module_name: str, module_path: str):
        dir_path = path.dirname(module_path)
        module_path = path.basename(module_path)

        android_root = None
        if self.android_root is not None:
            android_root = path.relpath(self.android_root, dir_path)
        module_paths_map = {}
        for src_module_path, dst_module_path in self.module_paths_map.items():
            dst_module_path = path.relpath(dst_module_path, dir_path)
            module_paths_map[src_module_path] = dst_module_path

        self.deinit()

        with TemporaryWorkingDirectory(dir_path):
            bazel_parser = BazelParser(
                android_root,
                module_paths_map,
                self.flags_map,
                self.debug,
                self.print_bazel_output,
            )

            bazel_parser.parse(module_path)

        self.init()

        for target in bazel_parser.targets.values():
            self.add_target(target, module_name)

    def import_module(self, module_path: str):
        module = import_module(module_path)
        assert module is not None
        return module

    def _lookup_target(self, target_spec: str):
        target = self.targets[target_spec]

        if not isinstance(target, Alias):
            return target

        module_name, _ = self.spec_resolution(target_spec)
        return self.targets[f"{module_name}:{target.actual}"]

    def lookup_target(self, target_spec: str) -> Rule:
        if target_spec in self.targets:
            return self._lookup_target(target_spec)

        module_name, module_path = self.spec_resolution(target_spec)
        if module_path:
            self.parse_module(module_name, module_path)

        return self._lookup_target(target_spec)

    def lookup_targets(self, t: type[T]) -> List[T]:
        found_targets = set()
        for target in self.targets.values():
            if isinstance(target, t):
                found_targets.add(target)
        return list(found_targets)

    def print_impl(
        self,
        *args,
        file: Optional[TextIOWrapper] = None,
        **kwargs,
    ):
        if file is not None and file.name == "<stderr>":
            self.original_print(*args, file=file, **kwargs)

    def select_impl(self, d: Dict[str, any]):
        default_value = None

        for cond_spec, cond_value in d.items():
            if cond_spec == "//conditions:default":
                default_value = cond_value
                continue

            if cond_spec in self.flags_map:
                return cond_value

            module_name, module_path = self.spec_resolution(cond_spec)
            if not module_path or not path.exists(module_path):
                self.original_print(f"Failed to load {cond_spec}")
                continue

            self.parse_module(module_name, module_path)

            if cond_spec not in self.targets:
                self.original_print(f"Failed to find config {cond_spec}")
                continue

            config_setting = self.lookup_target(cond_spec)
            assert isinstance(config_setting, ConfigSetting)

            assert len(config_setting.flag_values) == 1

            for flag_spec, flag_expected_value in config_setting.flag_values.items():
                flag = self.lookup_target(flag_spec)
                if isinstance(flag, BoolFlag):
                    flag_expected_value = BoolFlag.parse_value(flag_expected_value)
                    if flag.name not in self.flags_map:
                        continue

                    flag_value = self.flags_map[flag.name]
                    flag_value = BoolFlag.parse_value(flag_value)

                    if flag_value == flag_expected_value:
                        return cond_value
                else:
                    assert False

        return default_value

    def struct_impl(self, **kwargs):
        if self.debug:
            self.original_print("struct", kwargs)

        s = SimpleNamespace()
        for k, v in kwargs.items():
            setattr(s, k, v)

        return s

    def package_impl(self, *args, **kwargs):
        if self.debug:
            self.original_print("package", args, kwargs)

    def load_impl(
        self,
        file_spec: str,
        *names: List[str],
        **mapped_names: Dict[str, str],
    ):
        if self.debug:
            self.original_print("load", file_spec, names)

        _, module_path = self.spec_resolution(file_spec, target_is_file=True)
        if not module_path or not path.exists(module_path):
            self.original_print(f"Failed to load {file_spec}")
            return

        module = self.import_module(module_path)

        mapped_names.update({x: x for x in names})

        for name, src_name in mapped_names.items():
            if name in self.overriden_rules:
                self.original_print(f"Skipped overriden rule {name}")
                continue

            value = getattr(module, src_name)
            setattr(builtins, name, value)

    def add_target(self, target: Rule, module_name=""):
        assert target.name not in self.targets, f"Target {target.name} already exists"

        self.targets[f"{module_name}:{target.name}"] = target
        if not module_name:
            self.targets[target.name] = target

    def add_target_impl(self, t: type[T]):
        def _add_target_impl(**data):
            target = t(**data)
            if self.debug:
                self.original_print(target)
            self.add_target(target)

        return _add_target_impl

    def dummy(self, name: str):
        def dummy_impl(**data):
            if self.debug:
                self.original_print(name)
                self.original_print(data)
                self.original_print()

        return dummy_impl

    def rule_impl(self, **data):
        if self.debug:
            self.original_print("rule")
            self.original_print(data)
            self.original_print()

        def rule_callable(**data):
            if self.debug:
                self.original_print("rule_callable")
                self.original_print(data)
                self.original_print()

            def rule_inner_callable(**data):
                if self.debug:
                    self.original_print("rule_inner_callable")
                    self.original_print(data)
                    self.original_print()

            return rule_inner_callable

        return rule_callable

    def fail_impl(self, s: str):
        raise ValueError(s)

    def glob_impl(self, globs: List[str]):
        if self.debug:
            self.original_print("glob", globs)

        found_files = []
        for g in globs:
            g_files = glob(g, recursive=True)
            found_files.extend(g_files)

        return found_files

    def depset_wrapper(self, data: List[str]):
        if self.debug:
            self.original_print("depset", data)

        data.sort()

        return depset_impl(data)

    def native_glob_wrapper(self, *args, **kwargs):
        if self.debug:
            self.original_print("native_glob", args, kwargs)

        return native_glob_impl(*args, **kwargs)

    def init(self):
        for key, value in self.overriden_rules.items():
            setattr(builtins, key, value)

    def evaluate_genrule(self, genrule: GenRule):
        location_pattern = r"\$\(\s*location\s+(//[^\)]+)\s*\)"

        def replace(match):
            location_param = match.group(1)
            module_name, module_path = self.spec_resolution(location_param)
            print(module_name, module_path)
            return location_param

        print("before", genrule.cmd)
        genrule.cmd = re.sub(location_pattern, replace, genrule.cmd)
        print("after", genrule.cmd)

    def evaluate_genrules(self):
        genrules = self.lookup_targets(GenRule)
        for genrule in genrules:
            self.evaluate_genrule(genrule)

    def parse(self, file_path: str):
        self.init()
        import_module(file_path)
        self.deinit()

    def deinit(self):
        builtins.print = self.original_print

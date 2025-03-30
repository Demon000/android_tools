from typing import Dict, List, Optional


class Rule:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        s = f"{self.__class__.__name__}:\n"
        s += f"\tname: {self.name}\n"
        return s


class DdkHeaders(Rule):
    def __init__(
        self,
        *,
        name: str,
        hdrs: List[str],
        includes: Optional[List[str]] = None,
        visibility: Optional[List[str]] = None,
        linux_includes: Optional[List[str]] = None,
    ):
        super().__init__(name)

        self.hdrs = hdrs
        self.includes = includes
        self.visibility = visibility
        self.linux_includes = linux_includes

    def __str__(self):
        s = super().__str__()
        s += f"\thdrs: {self.hdrs}\n"
        s += f"\tincludes: {self.includes}\n"
        s += f"\tvisibility: {self.visibility}\n"
        s += f"\tlinux_includes: {self.linux_includes}\n"
        return s


class DdkModule(Rule):
    def __init__(
        self,
        *,
        name: str,
        deps: List[str],
        hdrs: Optional[List[str]] = None,
        srcs: Optional[List[str]] = None,
        conditional_srcs: Optional[List[str]] = None,
        local_defines: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
        kconfig: Optional[str] = None,
        defconfig: Optional[str] = None,
        kernel_build: Optional[str] = None,
        copts: Optional[List[str]] = None,
        out: Optional[List[str]] = None,
    ):
        super().__init__(name)

        self.srcs = srcs
        self.conditional_srcs = conditional_srcs
        self.local_defines = local_defines
        self.deps = deps
        self.hdrs = hdrs
        self.includes = includes
        self.kconfig = kconfig
        self.defconfig = defconfig
        self.kernel_build = kernel_build
        self.copts = copts
        self.out = out

    def __str__(self):
        s = super().__str__()
        s += f"\tsrcs: {self.srcs}\n"
        s += f"\tconditional_srcs: {self.conditional_srcs}\n"
        s += f"\tlocal_defines: {self.local_defines}\n"
        s += f"\tdeps: {self.deps}\n"
        s += f"\thdrs: {self.hdrs}\n"
        s += f"\tincludes: {self.includes}\n"
        s += f"\tkconfig: {self.kconfig}\n"
        s += f"\tdefconfig: {self.defconfig}\n"
        s += f"\tkernel_build: {self.kernel_build}\n"
        s += f"\tcopts: {self.copts}\n"
        s += f"\tout: {self.out}\n"
        return s


class DdkSubModule(Rule):
    def __init__(
        self,
        *,
        name: str,
        srcs: List[str],
        out: str,
        deps: List[str],
        local_defines: List[str],
        kernel_build: Optional[str] = None,
    ):
        super().__init__(name)

        self.srcs = srcs
        self.out = out
        self.deps = deps
        self.local_defines = local_defines
        self.kernel_build = kernel_build

    def __str__(self):
        s = super().__str__()
        s += f"\tsrcs: {self.srcs}\n"
        s += f"\tout: {self.out}\n"
        s += f"\tdeps: {self.deps}\n"
        s += f"\tlocal_defines: {self.local_defines}\n"
        s += f"\tkernel_build: {self.kernel_build}\n"
        return s


class GenRule(Rule):
    def __init__(
        self,
        *,
        name: str,
        srcs: List[str],
        outs: List[str],
        cmd: Optional[str] = None,
        cmd_bash: Optional[str] = None,
        tools: Optional[str] = None,
    ):
        super().__init__(name)

        self.cmd = cmd
        self.cmd_bash = cmd_bash
        self.tools = tools
        self.srcs = srcs
        self.outs = outs
        self.evaluated = False

    def __str__(self):
        s = super().__str__()
        s += f"\tcmd: {self.cmd}\n"
        s += f"\tcmd_bash: {self.cmd_bash}\n"
        s += f"\ttools: {self.tools}\n"
        s += f"\tsrcs: {self.srcs}\n"
        s += f"\touts: {self.outs}\n"
        return s


class Alias(Rule):
    def __init__(
        self,
        *,
        name: str,
        actual: str,
        deprecation: Optional[str] = None,
        visibility: Optional[List[str]] = None,
    ):
        super().__init__(name)

        self.actual = actual
        self.deprecation = deprecation
        self.visibility = visibility

    def __str__(self):
        s = super().__str__()
        s += f"\tactual: {self.actual}\n"
        s += f"\tdeprecation: {self.deprecation}\n"
        s += f"\tvisibility: {self.visibility}\n"
        return s


class BoolFlag(Rule):
    def __init__(
        self,
        *,
        name: str,
        build_setting_default: bool,
        visibility: Optional[List[str]] = None,
    ):
        super().__init__(name)

        self.build_setting_default = build_setting_default
        self.visibility = visibility

    def __str__(self):
        s = super().__str__()
        s += f"\tbuild_setting_default: {self.build_setting_default}\n"
        s += f"\tvisibility: {self.visibility}\n"
        return s

    @staticmethod
    def parse_value(value: str | bool) -> bool:
        if isinstance(value, bool):
            return value

        if value in ["0", "disabled", "false", "False"]:
            return False

        if value in ["1", "enabled", "true", "True"]:
            return True

        raise ValueError(f"Unknown bool {value}")


class ConfigSetting(Rule):
    def __init__(
        self,
        *,
        name: str,
        flag_values: Dict[str, str],
        visibility: List[str],
    ):
        super().__init__(name)

        self.flag_values = flag_values
        self.visibility = visibility

    def __str__(self):
        s = super().__str__()
        s += f"\tflag_values: {self.flag_values}\n"
        s += f"\tvisibility: {self.visibility}\n"
        return s

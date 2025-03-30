from typing import TextIO
from parser_impl import BazelParser, DdkModule, DdkSubModule, GenRule


def write_submodule_kbuild(
    o: TextIO,
    submodule: DdkSubModule | DdkModule,
    bazel_parser: BazelParser,
):
    if submodule.out is None:
        return

    module_obj_name = submodule.out
    assert module_obj_name.endswith(".ko")
    module_obj_name = module_obj_name[: -len(".ko")]

    o.write(f"obj-m += {module_obj_name}.o\n")

    for src in submodule.srcs:
        if src.startswith(":"):
            target = bazel_parser.lookup_target(src)
            assert isinstance(target, GenRule)
        elif src.endswith(".c"):
            src = src[: -len(".c")] + ".o"
            o.write(f"{module_obj_name}-y += {src}\n")
        elif src.endswith(".h"):
            continue
        else:
            assert False, src

    if (
        hasattr(submodule, "conditional_srcs")
        and submodule.conditional_srcs is not None
    ):
        # TODO
        pass

    cflags = []
    if submodule.local_defines is not None:
        for define in submodule.local_defines:
            cflags.append(f"-D{define}")
    if hasattr(submodule, "includes") and submodule.includes is not None:
        for include in submodule.includes:
            cflags.append(f"-I$(src)/{include}")
    if hasattr(submodule, "copts") and submodule.copts is not None:
        cflags += submodule.copts

    if cflags:
        o.write(f"CFLAGS_{module_obj_name}.o := \\\n")
        for cflag in cflags:
            o.write(f"\t{cflag}")
            if cflag is not cflags[-1]:
                o.write(" \\\n")
            else:
                o.write("\n")

    o.write("\n")


def _write_kbuild(o: TextIO, bazel_parser: BazelParser):
    ddk_modules = bazel_parser.lookup_targets(DdkModule)

    for ddk_module in ddk_modules:
        soc, variant, _ = ddk_module.name.split("_", 2)

        o.write(
            f"""
ifeq ($(CONFIG_ARCH_{soc.upper()}), y)
ifeq ($(CONFIG_LOCALVERSION, -{variant}))
""".lstrip()
        )

        write_submodule_kbuild(o, ddk_module, bazel_parser)

        for dep in ddk_module.deps:
            submodule = bazel_parser.lookup_target(dep)

            if isinstance(submodule, DdkSubModule):
                write_submodule_kbuild(o, submodule, bazel_parser)
            else:
                print(submodule)

        o.write(
            """
endif
endif
""".lstrip()
        )

        if ddk_module != ddk_modules[-1]:
            o.write("\n")


def write_kbuild(kbuild_path: str, bazel_parser: BazelParser):
    with open(kbuild_path, "w", encoding="utf-8") as o:
        _write_kbuild(o, bazel_parser)

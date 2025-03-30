_common_outs = [
    "System.map",
    "modules.builtin",
    "modules.builtin.modinfo",
    "vmlinux",
    "vmlinux.symvers",
]

DEFAULT_IMAGES = [
    "Image",
    "Image.lz4",
    "Image.gz",
]

DEFAULT_GKI_OUTS = _common_outs + DEFAULT_IMAGES
X86_64_OUTS = _common_outs + ["bzImage"]
aarch64_outs = DEFAULT_GKI_OUTS
x86_64_outs = X86_64_OUTS

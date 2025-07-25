import builtins
from contextlib import contextmanager
from enum import Enum
import importlib
from importlib.machinery import SourceFileLoader
import os
from typing import Generator


def import_module(module_path: str):
    module_name = module_path.strip("./").replace("/", "__").replace(".", "_")
    loader = SourceFileLoader(module_name, module_path)
    spec = importlib.util.spec_from_file_location(module_name, loader=loader)
    if spec is None:
        return None

    module = importlib.util.module_from_spec(spec)

    loader = spec.loader
    if loader is None:
        return None

    loader.exec_module(module)

    return module


@contextmanager
def TemporaryWorkingDirectory(dir_path: str) -> Generator[None, None, None]:
    cwd = os.getcwd()

    os.chdir(dir_path)

    try:
        yield
    finally:
        os.chdir(cwd)


class Color(str, Enum):
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    END = '\033[0m'


builtin_print = builtins.print

def color_print(*args, color: Color, **kwargs):
    args_str = ' '.join(str(arg) for arg in args)
    args_str = color.value + args_str + Color.END.value
    builtin_print(args_str, **kwargs)

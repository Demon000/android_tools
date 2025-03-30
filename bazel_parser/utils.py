from contextlib import contextmanager
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

import importlib
from importlib.machinery import SourceFileLoader


def import_module(module_path: str):
    module_name = module_path.strip('./').replace('/', '__').replace('.', '_')
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

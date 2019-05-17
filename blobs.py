import os

from utils import *

class Blob:
    def __init__(self, dir_path, path):
        absolute_path = os.path.join(dir_path, path)
        name = os.path.basename(path)

        self._absolute_path = absolute_path
        self._path = path
        self._name = name

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path

    def get_absolute_path(self):
        return self._absolute_path

class ELFBlob(Blob):
    def __init__(self, dir_path, path):
        super().__init__(dir_path, path)

        self._find_arch()

    def _find_arch(self):
        self._arch = get_arch(self._absolute_path)

    def get_arch(self):
        return self._arch

class ELFGroup():
    def __init__(self, dir_path, blobs):
        self._blobs = blobs
        self._main_blob = blobs[-1]

        self._find_arches()

    def _find_arches(self):
        self._arches = []
        for blob in self._blobs:
            arch = blob.get_arch()
            self._arches.append(arch)

    def get_name(self):
        return self._main_blob.get_name()

    def get_blobs(self):
        return self._blobs

    def get_arch_blobs(self, arches):
        arch_blobs = []
        for blob in self._blobs:
            if blob.get_arch() not in arches:
                continue

            arch_blobs.append(blob)

        return arch_blobs

    def find_used_libraries(self):
        path = self._main_blob.get_absolute_path()

        # A list for libraries we're still looking for
        needed_libraries = get_needed_libraries(path)
        dlopened_libraries = get_dlopened_libraries(path)
        self.library_names = needed_libraries + dlopened_libraries

        # Another list to be populated with ELF groups found for
        # the libraries we were looking for
        self.found_elf_blobs = []

    def get_missing_libraries(self):
        return self.library_names[:]

    def get_used_blobs(self):
        all_used_blobs = []

        all_used_blobs.extend(self._blobs)

        for elf_group in self.found_elf_blobs:
            arch_blobs = elf_group.get_arch_blobs(self._arches)
            all_used_blobs.extend(arch_blobs)

        return all_used_blobs

    def try_solve_dependencies(self, other):
        # If the shared library given to us matches a dependency we're looking
        # for, add it to the solved dependencies list and add its unsolved
        # dependencies to our list of unsolved dependencies
        # Arch is not checked here because we expect libraries to be available
        # for at least all the needed arches
        # (how else would they work in stock?)
        other_name = other.get_name()
        if other_name not in self.library_names:
            return False

        self.found_elf_blobs.append(other)
        self.library_names.remove(other_name)

        other_libraries = other.get_missing_libraries()
        self.library_names.extend(other_libraries)

        return True

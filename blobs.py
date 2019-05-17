import os

from utils import *

class Blob:
    def __init__(self, dir_path, path):
        absolute_path = os.path.join(dir_path, path)
        filename = os.path.basename(path)
        name = os.path.splitext(filename)[0]

        self._absolute_path = absolute_path
        self._path = path
        self._filename = filename
        self._name = name

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path

    def get_absolut_path(self):
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

    def _find_dependencies(self, path):
        # A list for libraries we're still looking for and another list
        # for ELF blobs found for the libraries we were looking for
        self.dependency_names = []
        self.dependencies = []

        # Add needed libraries found in the ELF header and dlopened
        # libraries found by scanning the rodata section of the file
        # to a list of libraries we're looking for
        needed_libraries = get_needed_libraries(path)
        dlopened_libraries = get_dlopened_libraries(path)
        libraries = needed_libraries + dlopened_libraries
        for library in libraries:
            # Remove extension
            name = library[:-3]

            self.dependency_names.append(name)

    def get_name(self):
        return self._main_blob.get_name()

    def get_blobs(self):
        return self._blobs

    def find_dependencies(self):
        # Dependencies are tracked for only one of the ELF files inside
        # the group
        path = self._main_blob.get_absolut_path()
        self._find_dependencies(path)

    def get_unsolved_dependency_names(self):
        return self.dependency_names[:]

    def get_found_elf_blobs(self):
        all_elf_blobs = []

        for dependency in self.dependencies:
            elf_blobs = dependency.get_blobs()
            for elf_blob in elf_blobs:
                arch = elf_blob.get_arch()
                if arch not in self._arches:
                    continue

                all_elf_blobs.append(elf_blob)

        return all_elf_blobs

    def try_solve_dependencies(self, other):
        # If the shared library given to us matches a dependency we're looking
        # for, add it to the solved dependencies list and add its unsolved
        # dependencies to our list of unsolved dependencies
        # Arch is not checked here because we expect libraries to be available
        # for at least all the needed arches
        # (how else would they work in stock?)
        other_name = other.get_name()
        if other_name not in self.dependency_names:
            return False

        self.dependencies.append(other)
        self.dependency_names.remove(other_name)

        new_dependencies = other.get_unsolved_dependency_names()
        self.dependency_names.extend(new_dependencies)

        return True

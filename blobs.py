import os

from utils import *

class CommonBlobInterface:
    def get_needed_blobs(self):
        return self._needed_blobs

    def get_strings(self):
        return self._strings

    def _is_needed_blob(self, other):
        name = other.get_name()
        if name in self._needed_blobs:
            return True

        for string in self._strings:
            if name in string:
                return True

        return False

    def _adopt_blobs(self, other):
        # ELF groups aren't real blobs so don't add them to
        # the list of blobs, but add the blobs they contain.
        if isinstance(other, ELFGroup):
            blobs = other.get_initial_blobs()
            self._blobs.extend(blobs)
        elif isinstance(other, ELFBlob) or isinstance(other, Blob):
            self._blobs.append(other)

        needed_blobs = other.get_needed_blobs()
        found_blobs = other.get_found_blobs()
        strings = other.get_strings()

        self._needed_blobs.extend(needed_blobs)
        self._blobs.extend(found_blobs)
        self._strings.extend(strings)

    def try_needed_blob(self, other):
        if self == other:
            return False

        if other in self._blobs:
            return False

        if not self._is_needed_blob(other):
            return False

        self._adopt_blobs(other)

        return True

    def get_found_blobs(self):
        return self._blobs[:]

class Blob(CommonBlobInterface):
    def __init__(self, dir_path, path):
        absolute_path = os.path.join(dir_path, path)
        name = os.path.basename(path)

        self._absolute_path = absolute_path
        self._path = path
        self._name = name
        self._blobs = []

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path

    def get_absolute_path(self):
        return self._absolute_path

    def find_needed_blobs(self):
        self._needed_blobs = []
        self._strings = get_strings(self._absolute_path)

class ELFBlob(Blob):
    def __init__(self, dir_path, path):
        super().__init__(dir_path, path)

        self._find_arch()

    def _find_arch(self):
        self._arch = get_arch(self._absolute_path)

    def get_arch(self):
        return self._arch

    def set_needed_blobs(self, needed_blobs):
        self._needed_blobs = needed_blobs

    def set_strings(self, strings):
        self._strings = strings

    def find_needed_blobs(self):
        self._needed_blobs = get_needed_libraries(self._absolute_path)
        self._strings = get_rodata_strings(self._absolute_path)

class ELFGroup(CommonBlobInterface):
    def __init__(self, dir_path, blobs):
        self._blobs = blobs[:]
        self._initial_blobs = blobs[:]

    def get_name(self):
        return self._initial_blobs[0].get_name()

    def get_initial_blobs(self):
        return self._initial_blobs[:]

    def find_needed_blobs(self):
        path = self._initial_blobs[0].get_absolute_path()
        self._needed_blobs = get_needed_libraries(path)
        self._strings = get_rodata_strings(path)

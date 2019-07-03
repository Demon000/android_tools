import os

from utils import *

class CommonBlobInterface:
    def __init__(self):
        self._blobs = set()

    def _is_service_init_file(self, other):
        path = self.get_absolute_path()
        if not path.startswith("bin/"):
            return False

        name = self.get_name()
        other_name = other.get_name()
        if name + ".rc" == other.get_name():
            return True

        return False

    def _is_other_name_inside(self, other):
        other_name = other.get_name()
        blobs = [self] + list(self._blobs)
        for blob in blobs:
            blob_path = blob.get_absolute_path()

            if path_contains_string(blob_path, other_name):
                return True

        return False

    def _is_needed_blob(self, other):
        if self._is_service_init_file(other):
            return True

        if self._is_other_name_inside(other):
            return True

        return False

    def try_needed_blob(self, other):
        if not self._is_needed_blob(other):
            return False

        found_blobs = other.get_found_blobs()
        self._blobs.update(found_blobs)
        self._blobs.add(other)

        return True

    def get_found_blobs(self):
        return self._blobs

    def get_blob_list(self):
        # Get the target arches of top-most blob
        if isinstance(self, ELFGroup):
            target_arches = self.get_arches()
        elif isinstance(self, ELFBlob):
            arch = self.get_arch()
            target_arches = [arch]
        else:
            target_arches = []

        # Unpack ELFGroups
        blobs = [self] + list(self._blobs)
        unpacked_blobs = []
        for blob in blobs:
            if isinstance(blob, ELFGroup):
                initial_blobs = blob.get_initial_blobs()
                unpacked_blobs.extend(initial_blobs)
            else:
                unpacked_blobs.append(blob)

        if not target_arches:
            return unpacked_blobs

        final_blobs = []
        for blob in unpacked_blobs:
            if isinstance(blob, ELFBlob):
                arch = blob.get_arch()
                if arch not in target_arches:
                    continue

            final_blobs.append(blob)

        return final_blobs

class Blob(CommonBlobInterface):
    def __init__(self, dir_path, path):
        super().__init__()

        absolute_path = os.path.join(dir_path, path)
        name = os.path.basename(path)
        module_name = os.path.splitext(name)[0]

        self._absolute_path = absolute_path
        self._path = path
        self._name = name
        self._module_name = module_name

    def get_name(self):
        return self._name

    def get_module_name(self):
        return self._module_name

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

class ELFGroup(CommonBlobInterface):
    def __init__(self, dir_path, blobs):
        super().__init__()

        self._initial_blobs = blobs

    def get_name(self):
        return self._initial_blobs[0].get_name()

    def get_module_name(self):
        return self._initial_blobs[0].get_module_name()

    def get_arches(self):
        arches = []

        for blob in self._initial_blobs:
            arch = blob.get_arch()
            arches.append(arch)

        return arches

    def get_absolute_path(self):
        return self._initial_blobs[0].get_absolute_path()

    def get_initial_blobs(self):
        return self._initial_blobs

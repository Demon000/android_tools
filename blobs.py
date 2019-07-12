import os

from utils import *


class CommonBlobInterface:
    def __init__(self):
        self._blobs = []

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
        path = self.get_absolute_path()
        other_name = other.get_name()

        if path_contains_string(path, other_name):
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

        self._blobs.append(other)

        return True

    def get_blob_list(self):
        # Get the target arches of top-most blob
        target_arches = self.get_arches()

        # Unpack ELFGroups
        packed_blobs = [self] + self._blobs
        unpacked_blobs = []
        for blob in packed_blobs:
            contained_blobs = blob.get_contained_blobs()
            unpacked_blobs.extend(contained_blobs)

        if not target_arches:
            return unpacked_blobs

        final_blobs = []
        for blob in unpacked_blobs:
            if not blob.is_matching_arch(target_arches):
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

    def get_contained_blobs(self):
        return [self]

    def get_arches(self):
        return []

    def is_matching_arch(arches):
        return True


class ELFBlob(Blob):
    def __init__(self, dir_path, path):
        super().__init__(dir_path, path)

        self._arch = get_arch(self._absolute_path)

    def get_arches(self):
        return [self._arch]

    def is_matching_arch(arches):
        return self._arch in arches


class ELFGroup(CommonBlobInterface):
    def __init__(self, _, blobs):
        super().__init__()

        self._contained_blobs = blobs
        self._arches = []
        for blob in self._contained_blobs:
            blob_arches = blob.get_arches()
            self._arches.extend(blob_arches)

    def get_contained_blobs(self):
        return self._contained_blobs

    def get_blob(self):
        return self._contained_blobs[0]

    def get_name(self):
        return self.get_blob().get_name()

    def get_module_name(self):
        return self.get_blob().get_module_name()

    def get_absolute_path(self):
        return self.get_blob().get_absolute_path()

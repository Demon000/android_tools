import os

from utils import *


class GenericBlob:
    def __init__(self):
        self._blobs = []

    def get_name(self):
        raise NotImplementedError()

    def get_absolute_path(self):
        raise NotImplementedError()

    def get_arches(self):
        raise NotImplementedError()

    def is_init_file(self):
        return self.get_name().endswith(".rc")

    def is_service_file(self):
        return "/bin/" in self.get_absolute_path()

    def is_other_name_inside(self, other):
        path = self.get_absolute_path()
        other_name = other.get_name()

        if path_contains_string(path, other_name):
            return True

        return False

    def _is_needed_blob(self, other):
        # No .rc file should be the head of the hierarchy
        if self.is_init_file():
            return False

        # .rc files should be marked as dependencies if they contain this name
        if self.is_service_file() and other.is_init_file() and \
                other.is_other_name_inside(self):
            return True

        if self.is_other_name_inside(other):
            return True

        return False

    def try_needed_blob(self, other):
        if not self._is_needed_blob(other):
            return False

        self._blobs.append(other)

        return True

    def get_blob_list(self):
        # Unpack ELFGroups
        unpacked_blobs = []
        for blob in self._blobs:
            contained_blobs = blob.get_contained_blobs()
            unpacked_blobs.extend(contained_blobs)

        # Get the target arches of top-most blob
        target_arches = self.get_arches()
        if not target_arches:
            return unpacked_blobs

        final_blobs = []
        for blob in unpacked_blobs:
            if not blob.is_matching_arch(target_arches):
                continue

            final_blobs.append(blob)

        return final_blobs


class Blob(GenericBlob):
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

    def is_matching_arch(self, arches):
        return True

    def set_blobs(self, blobs):
        self._blobs = blobs


class ELFBlob(Blob):
    def __init__(self, dir_path, path):
        super().__init__(dir_path, path)

        self._arch = get_arch(self._absolute_path)

    def get_arches(self):
        return [self._arch]

    def is_matching_arch(self, arches):
        return self._arch in arches


class ELFGroup(GenericBlob):
    def __init__(self, _, blobs):
        super().__init__()

        self._contained_blobs = blobs
        self._arches = []
        for blob in self._contained_blobs:
            blob_arches = blob.get_arches()
            self._arches.extend(blob_arches)

    def get_arches(self):
        return self._arches

    def get_contained_blobs(self):
        for blob in self._contained_blobs:
            blob.set_blobs(self._blobs)

        return self._contained_blobs

    def get_blob(self):
        return self._contained_blobs[0]

    def get_name(self):
        return self.get_blob().get_name()

    def get_module_name(self):
        return self.get_blob().get_module_name()

    def get_absolute_path(self):
        return self.get_blob().get_absolute_path()

#!/usr/bin/python

import sys

from blobs import *


class BlobList:
    def __init__(self, dir_path):
        self.__dir_path = dir_path
        self.__modules = self._read_modules()
        self.__blacklisted = self._read_blacklisted()

        all_file_paths = self._get_dir_file_paths(self.__dir_path)

        executable_blobs = self._extract_elf_blobs(all_file_paths, ["bin/"])
        lib_groups = self._extract_elf_groups(all_file_paths, ["lib/", "lib64/"])
        all_blobs = self._extract_blobs(all_file_paths, [])

        blobs = executable_blobs + lib_groups + all_blobs
        adopted_blobs = []

        # Figure out non-elf dependencies
        current_adopted_blobs = self._adopt_blobs(blobs, all_blobs)
        adopted_blobs.extend(current_adopted_blobs)

        # Figure out elf dependencies
        current_adopted_blobs = self._adopt_blobs(blobs, lib_groups)
        adopted_blobs.extend(current_adopted_blobs)

        for adopted_blob in adopted_blobs:
            blobs.remove(adopted_blob)

        self._blobs = blobs

    @staticmethod
    def _read_modules():
        with open("source_available_files.txt", "r") as file:
            modules = file.read().splitlines()

        return modules

    @staticmethod
    def _read_blacklisted():
        with open("blacklisted_files.txt", "r") as file:
            blacklisted = file.read().splitlines()

        return blacklisted

    @staticmethod
    def _get_dir_file_paths(dir_path):
        """
        Get a list of file paths found inside `dir_path`.

        Args:
            dir_path (str): A path to a directory to look inside.

        Returns:
            list: A list of all the file paths.
        """

        file_paths = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                absolute_file_path = os.path.join(root, file)
                if os.path.islink(absolute_file_path):
                    continue

                relative_file_path = os.path.relpath(absolute_file_path, dir_path)
                file_paths.append(relative_file_path)

        return file_paths

    @staticmethod
    def _extract_subdir_file_paths(file_paths, subdirs):
        """
        Extract file paths that are found under `subdir` from a list of file paths.

        Args:
            file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted file paths.
        """

        subdir_file_paths = []

        for file_path in file_paths:
            if subdirs:
                found_in_subdirs = False

                for subdir in subdirs:
                    if file_path.startswith(subdir):
                        found_in_subdirs = True
                        break

                if not found_in_subdirs:
                    continue

            subdir_file_paths.append(file_path)

        for file_path in subdir_file_paths:
            file_paths.remove(file_path)

        return subdir_file_paths

    def _extract_blobs(self, all_file_paths, subdirs):
        """
        Extract a list of simple blobs from the file paths that are
        found under `subdir` from a list of file paths.

        Args:
            all_file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted simple blobs.
        """

        blobs = []

        file_paths = self._extract_subdir_file_paths(all_file_paths, subdirs)
        for file_path in file_paths:
            try:
                blob = Blob(self.__dir_path, file_path)
                if blob.get_name() in self.__blacklisted:
                    continue

                blobs.append(blob)
            except:
                pass

        return blobs

    def _extract_elf_blobs(self, all_file_paths, subdirs):
        """
        Extract a list of elf blobs from the file paths that are
        found under `subdir` from a list of file paths.

        Args:
            all_file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted elf blobs.
        """

        elf_blobs = []
        non_elf_file_paths = []

        file_paths = self._extract_subdir_file_paths(all_file_paths, subdirs)
        for file_path in file_paths:
            try:
                elf_blob = ELFBlob(self.__dir_path, file_path)
                elf_blobs.append(elf_blob)
            except:
                non_elf_file_paths.append(file_path)

        # Add back non-ELF files
        for file_path in non_elf_file_paths:
            all_file_paths.append(file_path)

        return elf_blobs

    def _extract_elf_groups(self, all_file_paths, subdirs):
        """
        Extract a list of elf groups from the file paths that are
        found under `subdir` from a list of file paths.

        Args:
            all_file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted elf groups.
        """

        nonelf_file_paths = []

        name_blobs = {}
        file_paths = self._extract_subdir_file_paths(all_file_paths, subdirs)
        for file_path in file_paths:
            try:
                elf_blob = ELFBlob(self.__dir_path, file_path)
                name_blobs.setdefault(elf_blob.get_name(), []).append(elf_blob)
            except:
                nonelf_file_paths.append(file_path)

        # Add back non-ELF files
        for file_path in nonelf_file_paths:
            all_file_paths.append(file_path)

        elf_groups = []
        for name, blobs in name_blobs.items():
            elf_group = ELFGroup(self.__dir_path, blobs)
            elf_groups.append(elf_group)

        return elf_groups

    @staticmethod
    def _adopt_blobs(target_blobs, source_blobs):
        """
        Adopt needed blobs from a list of blobs.

        Args:
            target_blobs (list): The list of blobs to adopt into.
            source_blobs (list): The list of blobs to adopt from.
        """
        adopted_blobs = []

        for source_blob in source_blobs:
            solved_any = False

            for target_blob in target_blobs:
                if source_blob == target_blob:
                    continue

                solved_one = target_blob.try_needed_blob(source_blob)
                if solved_one:
                    solved_any = True

            if solved_any:
                adopted_blobs.append(source_blob)

        return adopted_blobs

    def _print_blob(self, visited_blobs, blob, depth, file):
        visited_blobs.append(blob)

        indent = "\t" * depth
        file.write("{} {}\n", indent, blob_path)

        blob_items = blob.get_blob_list()
        for blob_item in blob_items:
            if blob_item not in visited_blobs:
                self._print_blob(visited_blobs, blob_item, depth + 1, file)

    def print_blob(self, blob, file):
        visited_blobs = []

        blob_module_name = blob.get_module_name()
        file.write("# {}\n".format(blob_module_name))

        blob_items = blob.get_blob_list()
        for blob_item in blob_items:
            self._print_blob(visited_blobs, blob, 0, file)

    def print_blobs(self, file):
        for blob in self._blobs:
            self.print_blob(blob, file)

    def print_modules(self, file):
        for blob in self._blobs:
            blob_name = blob.get_name()
            blob_module_name = blob.get_module_name()

            module_names = []
            blob_list = blob.get_blob_list()
            for blob_item in blob_list:
                blob_item_module_name = blob_item.get_module_name()
                if blob_item_module_name not in self.__modules:
                    continue

                if blob_item_module_name in module_names:
                    continue

                module_names.append(blob_item_module_name)

            if not len(module_names):
                continue

            module_names.sort()
            file.write("# modules for {}\n".format(blob_name))
            string = "PRODUCT_PACKAGES += \\\n"
            for module_name in module_names[:-1]:
                string += "\t" + module_name + " \\\n"

            last_module_name = module_names[-1]
            string += "\t" + last_module_name + "\n"

            file.write(string)
            file.write("\n")


if len(sys.argv) < 2:
    print("not enough arguments!")
    print("usage: blob_list.py <vendor_path> <target_path>")
    exit()

vendor_path = sys.argv[1]
target_path = sys.argv[2]

if not os.path.exists(target_path):
    os.makedirs(target_path)

target_proprietary_files_path = os.path.join(target_path, "proprietary_files.txt")
target_modules_path = os.path.join(target_path, "modules.mk")

blob_list = BlobList(vendor_path)
with open(target_proprietary_files_path, "w") as file:
    blob_list.print_blobs(file)

with open(target_modules_path, "w") as file:
    blob_list.print_modules(file)

#!/usr/bin/python

import os
import sys
import subprocess

from blobs import *

class BlobList:
    def __init__(self, dir_path):
        self.__dir_path = dir_path
        self.__modules = self._read_modules()
        self.__blacklisted = self._read_blacklisted()

    def _read_modules(self):
        with open("source_available_files.txt", "r") as file:
            modules = file.read().splitlines()

        return modules

    def _read_blacklisted(self):
        with open("blacklisted_files.txt", "r") as file:
            blacklisted = file.read().splitlines()

        return blacklisted

    def _get_dir_file_paths(self, dir_path):
        '''
        Get a list of file paths found inside `dir_path`.

        Args:
            dir_path (str): A path to a directory to look inside.

        Returns:
            list: A list of all the file paths.
        '''

        file_paths = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                absolute_file_path = os.path.join(root, file)
                if os.path.islink(absolute_file_path):
                    continue

                relative_file_path = os.path.relpath(absolute_file_path, dir_path)
                file_paths.append(relative_file_path)

        return file_paths

    def _extract_subdir_file_paths(self, file_paths, subdirs):
        '''
        Extract file paths that are found under `subdir` from a list of file paths.

        Args:
            file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted file paths.
        '''

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
        '''
        Extract a list of simple blobs from the file paths that are
        found under `subdir` from a list of file paths.

        Args:
            all_file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted simple blobs.
        '''

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
        '''
        Extract a list of elf blobs from the file paths that are
        found under `subdir` from a list of file paths.

        Args:
            all_file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted elf blobs.
        '''

        elf_blobs = []
        nonelf_file_paths = []

        file_paths = self._extract_subdir_file_paths(all_file_paths, subdirs)
        for file_path in file_paths:
            try:
                elf_blob = ELFBlob(self.__dir_path, file_path)
                elf_blobs.append(elf_blob)
            except:
                nonelf_file_paths.append(file_path)

        # Add back non-ELF files
        for file_path in nonelf_file_paths:
            all_file_paths.append(file_path)

        return elf_blobs

    def _extract_elf_groups(self, all_file_paths, subdirs):
        '''
        Extract a list of elf groups from the file paths that are
        found under `subdir` from a list of file paths.

        Args:
            all_file_paths (list): A list of file paths to extract from.
            subdirs (list): A list of subdirs to match.

        Returns:
            list: A list of all the extracted elf groups.
        '''

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

    def _adopt_blobs(self, target_blobs, source_blobs):
        '''
        Adopt needed blobs from a list of blobs.

        Args:
            target_blobs (list): The list of blobs to adopt into.
            source_blobs (list): The list of blobs to adopt from.
        '''
        i = 0
        while True:
            if i == len(source_blobs):
                break

            solved_any = False
            source_blob = source_blobs[i]
            for target_blob in target_blobs:
                if source_blob == target_blob:
                    continue

                solved_one = target_blob.try_needed_blob(source_blob)
                if solved_one:
                    solved_any = True

            if solved_any:
                source_blobs.pop(i)
            else:
                i += 1

    def build_blob_trees(self):
        all_file_paths = self._get_dir_file_paths(self.__dir_path)

        self._lib_groups = self._extract_elf_groups(all_file_paths, ["lib/", "lib64/"])
        self._executable_blobs = self._extract_elf_blobs(all_file_paths, ["bin/"])
        self._all_blobs = self._extract_blobs(all_file_paths, [])

        # Figure out dependencies between libs
        self._adopt_blobs(self._lib_groups, self._lib_groups)

        # Figure out dependencies of other files
        self._adopt_blobs(self._all_blobs, self._lib_groups)

        # Figure out dependencies of executables
        self._adopt_blobs(self._executable_blobs, self._lib_groups)
        self._adopt_blobs(self._executable_blobs, self._all_blobs)

    def print_blobs(self, file):
        blobs = self._executable_blobs + self._lib_groups + self._all_blobs

        for blob in blobs:
            blob_name = blob.get_name()
            blob_module_name = blob.get_module_name()

            if blob_name in self.__modules:
                continue

            blob_paths = []
            blob_items = blob.get_blob_list()
            for blob_item in blob_items:
                blob_item_module_name = blob_item.get_module_name()
                if blob_item_module_name in self.__modules:
                    continue

                blob_item_path = blob_item.get_path()
                blob_paths.append(blob_item_path)

            blob_paths.sort()
            file.write("# blobs for {}\n".format(blob_module_name))
            for blob_path in blob_paths:
                file.write("{}\n".format(blob_path))
            file.write("\n")

    def print_packages(self, file, blobs):
        module_names = []
        for blob in blobs:
            blob_module_name = blob.get_module_name()
            if blob_module_name not in module_names:
                module_names.append(blob_module_name)

        module_names.sort()
        string = "PRODUCT_PACKAGES += \\\n"
        for module_name in module_names[:-1]:
            string += "\t" + module_name + " \\\n"

        last_module_name = module_names[-1]
        string += "\t" + last_module_name + "\n"

        file.write(string)

    def print_modules(self, file):
        blobs = self._executable_blobs + self._lib_groups + self._all_blobs

        for blob in blobs:
            blob_name = blob.get_name()
            blob_module_name = blob.get_module_name()

            modules_list = []
            blob_list = blob.get_blob_list()
            for blob_item in blob_list:
                blob_item_module_name = blob_item.get_module_name()
                if blob_item_module_name in self.__modules:
                    modules_list.append(blob_item)

            if not len(modules_list):
                continue

            file.write("# modules for {}\n".format(blob_name))
            self.print_packages(file, modules_list)
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
blob_list.build_blob_trees()
with open(target_proprietary_files_path, "w") as file:
    blob_list.print_blobs(file)

with open(target_modules_path, "w") as file:
    blob_list.print_modules(file)

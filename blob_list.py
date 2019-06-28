#!/usr/bin/python

import os
import sys
import subprocess

from blobs import *

class BlobList:
    def __init__(self, dir_path):
        self.__dir_path = dir_path
        self.__blobs = []

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

        lib_groups = self._extract_elf_groups(all_file_paths, ["lib/", "lib64/"])
        executable_blobs = self._extract_elf_blobs(all_file_paths, ["bin/"])
        all_blobs = self._extract_blobs(all_file_paths, [])

        self._adopt_blobs(lib_groups, lib_groups)
        self._adopt_blobs(executable_blobs, lib_groups)
        self._adopt_blobs(executable_blobs, all_blobs)

        blob_usage_map = {}
        blobs = executable_blobs + lib_groups + all_blobs

        for blob in blobs:
            blob_list = blob.get_blob_list()
            for blob_item in blob_list:
                path = blob_item.get_path()
                if path not in blob_usage_map:
                    blob_usage_map[path] = 0

                blob_usage_map[path] += 1

        for blob in blobs:
            blob_list = blob.get_blob_list()
            first_blob = blob_list[0]
            print("# blobs for {}".format(first_blob.get_name()))
            for blob_item in blob_list:
                path = blob_item.get_path()
                if blob_usage_map[path] == 1:
                    print(path)

            print()

        for blob in blobs:
            blob_list = blob.get_blob_list()
            first_blob = blob_list[0]
            print("# common blobs for {}".format(first_blob.get_name()))
            for blob_item in blob_list:
                path = blob_item.get_path()
                if blob_usage_map[path] > 1:
                    print(path)

            print()

if len(sys.argv) < 2:
    print("not enough arguments!")
    print("usage: blob_list.py <vendor_path>")
    exit()

path = sys.argv[1]

blob_list = BlobList(path)
blob_list.build_blob_trees()

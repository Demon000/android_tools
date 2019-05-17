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

    def _flatten_elf_groups(self, elf_groups):
        '''
        Flatten a list of elf blobs.

        Args:
            elf_groups (list): The list of elf groups to flatten.
        '''
        i = 0
        while True:
            if i == len(elf_groups):
                break

            solved_any = False
            source_elf = elf_groups[i]
            for target_elf in elf_groups:
                solved_one = target_elf.try_solve_dependencies(source_elf)
                if solved_one:
                    solved_any = True

            if solved_any:
                elf_groups.pop(i)
            else:
                i += 1

    def build_blob_trees(self):
        all_file_paths = self._get_dir_file_paths(self.__dir_path)

        executable_groups = self._extract_elf_groups(all_file_paths, ["bin/"])
        lib_groups = self._extract_elf_groups(all_file_paths, ["lib/", "lib64/"])

        elf_groups = executable_groups + lib_groups

        for elf_group in elf_groups:
            elf_group.find_used_libraries()

        self._flatten_elf_groups(elf_groups)

        for elf_group in elf_groups:
            elf_blobs = elf_group.get_used_blobs()
            for elf_blob in elf_blobs:
                print(elf_blob.get_path())

            # libraries = elf_group.get_missing_libraries()
            # for library in libraries:
            #     print("ignoring: {}".format(library))

            print()

        print(len(executable_groups))
        print(len(lib_groups))

if len(sys.argv) < 2:
    print("Invalid number of arguments.")
    exit()

path = sys.argv[1]

blob_list = BlobList(path)
blob_list.build_blob_trees()

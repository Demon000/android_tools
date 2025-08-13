# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def parse_classmap_text(classmap_text: str):
    classmap: Dict[str, List[str]] = {}
    class_name = None

    for line in classmap_text.splitlines():
        if line.startswith('#'):
            continue

        line = line.strip()
        if not line:
            continue

        if line.startswith('class '):
            parts = line.split()
            assert len(parts) >= 2
            class_name = parts[1]
            classmap[class_name] = []
            continue

        if class_name is None:
            continue

        parts = line.split()
        assert len(parts) >= 1
        perm_name = parts[0]
        classmap[class_name].append(perm_name)

    return classmap


class Classmap:
    def __init__(self, classmap_path: str):
        classmap_text = Path(classmap_path).read_text()
        self.__class_perms_map = parse_classmap_text(classmap_text)
        self.__class_index_map: Dict[str, int] = {}
        self.__class_perms_index_map: Dict[str, Dict[str, int]] = {}

        for index, class_name in enumerate(self.__class_perms_map.keys()):
            self.__class_index_map[class_name] = index

            for perm_index, perm_name in enumerate(
                self.__class_perms_map[class_name]
            ):
                self.__class_perms_index_map.setdefault(class_name, {})
                self.__class_perms_index_map[class_name][perm_name] = perm_index

    def class_index(self, class_name: str):
        default = len(self.__class_index_map)
        return self.__class_index_map.get(class_name, default)

    def perm_index(self, class_name: str, perm_name: str):
        if class_name not in self.__class_index_map:
            return 0

        perms_map = self.__class_perms_index_map[class_name]

        if perm_name not in perms_map:
            return len(perms_map)

        return perms_map[perm_name]

    def sort_classes(self, classes: List[str]):
        classes.sort(key=lambda c: self.class_index(c))

    def sort_perms(self, class_name: str, perms: List[str]):
        perms.sort(key=lambda p: self.perm_index(class_name, p))

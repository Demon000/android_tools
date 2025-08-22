# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0


from enum import Enum


def remove_comments(line: str):
    index = line.find('#')
    if index != -1:
        line = line[:index]

    return line


def is_empty_line(line: str):
    return not line


def split_normalize_text(text: str):
    lines = text.splitlines(keepends=True)
    lines = map(remove_comments, lines)
    lines = list(filter(lambda line: not is_empty_line(line), lines))
    return lines

class Color(str, Enum):
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    END = '\033[0m'


def color_print(*args, color: Color, **kwargs):
    args_str = ' '.join(str(arg) for arg in args)
    args_str = color.value + args_str + Color.END.value
    print(args_str, **kwargs)

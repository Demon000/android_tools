# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0


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

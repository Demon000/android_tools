import string

from elftools.elf.elffile import ELFFile

def get_arch(path):
    with open(path, "rb") as file:
        elffile = ELFFile(file)
        return elffile.structs.elfclass

def get_needed_libraries(path):
    with open(path, "rb") as file:
        elffile = ELFFile(file)

        dynamic_section = elffile.get_section_by_name('.dynamic')
        if not dynamic_section:
            return []

        libraries = []
        for tag in dynamic_section.iter_tags():
            if tag.entry.d_tag == 'DT_NEEDED':
                libraries.append(tag.needed)

        return libraries

def get_rodata(path):
    with open(path, "rb") as file:
        elffile = ELFFile(file)

        rodata_section = elffile.get_section_by_name('.rodata')
        if not rodata_section:
            return bytes()

        return rodata_section.data()

def get_rodata_strings(rodata, min_len=4):
    strings = []

    result = ""
    for byte in rodata:
        char = chr(byte)

        # If char is printable then it can be a valid string
        if char in string.printable:
            result += char
            continue

        # If char is not printable then we're at the end of a string
        # Only take into account strings larger than `min_len`
        if len(result) >= min_len:
            strings.append(result)

        # Empty out the current string
        result = ""

    return strings

def get_library_strings(strings):
    libraries = []
    for s in strings:
        # Must end in `.so`
        if not s.endswith(".so"):
            continue

        # Ignore wildcard libraries
        if "%s" in s:
            continue

        # String with spaces must be a debug message
        if " " in s:
            continue

        libraries.append(s)

    return libraries

def get_dlopened_libraries(path):
    rodata = get_rodata(path)
    strings = get_rodata_strings(rodata)
    libraries = get_library_strings(strings)
    return libraries

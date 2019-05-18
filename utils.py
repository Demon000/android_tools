from string import printable

from elftools.elf.elffile import ELFFile

def get_printable_strings(binary_data, min_len=4):
    strings = []

    string = ""
    for byte in binary_data:
        char = chr(byte)

        if char in printable:
            string += char
            continue

        if len(string) >= min_len:
            strings.append(string)

        string = ""

    return strings

def get_strings(path):
    with open(path, "rb") as file:
        binary_data = file.read()

    return get_printable_strings(binary_data)

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

def get_rodata_strings(path, min_len=4):
    with open(path, "rb") as file:
        elffile = ELFFile(file)

        rodata_section = elffile.get_section_by_name('.rodata')
        if rodata_section:
            binary_data = rodata_section.data()
        else:
            binary_data = bytes()

    return get_printable_strings(binary_data)


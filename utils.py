data_map = {}


def get_arch(path):
    elf_magic32 = b'\x7fELF\x01'
    elf_magic64 =  b'\x7fELF\x02'

    with open(path, "rb") as file:
        file_head = file.read(5)

    if file_head == elf_magic32:
        return "32"

    if file_head == elf_magic64:
        return "64"

    raise ValueError()


def path_contains_string(path, string):
    binary_string = bytes(string, 'UTF-8')

    if path in data_map:
        binary_data = data_map[path]
    else:
        with open(path, "rb") as file:
            binary_data = file.read()
        data_map[path] = binary_data

    position = binary_data.find(binary_string)
    if position == -1:
        return False
    else:
        return True

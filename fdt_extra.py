import fdt

def line_offset(tabsize, offset, string):
    offset = ' ' * (tabsize * offset)
    return offset + string

class PropWordsWithPhandles(fdt.PropWords):
    def __init__(self, name, *args):
        super().__init__(name, *args)

        self.__phandle_names = {}

    def set_phandle_name(self, i, name):
        if i in self.__phandle_names:
            raise ValueError()

        self.__phandle_names[i] = name

    def get_phandle_name(self, i):
        return self.__phandle_names[i]

    def get_dts_value(self, i, word):
        if i in self.__phandle_names:
            return f'&{self.__phandle_names[i]}'
        else:
            return '0x{:X}'.format(word)

    def to_dts(self, tabsize: int = 4, depth: int = 0):
        result  = line_offset(tabsize, depth, self.name)
        result += ' = <'
        result += ' '.join([self.get_dts_value(i, word) for i, word in enumerate(self.data)])
        result += ">;\n"
        return result

import os
import re
import codecs


class CodeSection(object):
    def __init__(self, offset=None, length=None):
        self.offset = offset
        self.length = length

    def extend(self, length):
        self.length += length

    def load(self, o):
        self.offset = o["offset"]
        self.length = o["length"]

    def dump(self):
        return {
            "offset": self.offset,
            "length": self.length
        }


class Symbol(object):
    def __init__(self, name):
        self.name = name
        self.file_name = None
        self.sections = []
        self.tails = {}
        self.lines = {}

    def dump(self):
        o = {
            "file_name": self.file_name,
            "lines": self.lines
        }

        sections = []
        o["sections"] = sections

        for section in self.sections:
            sections.append(section.dump())

        return o

    def load(self, o):
        self.file_name = o["file_name"]
        self.lines = {
            int(key): value
            for key, value in o["lines"].items()
        }
        self.sections = []

        for section in o["sections"]:
            s = CodeSection()
            s.load(section)
            self.sections.append(s)

    def code(self, offset, length):
        section = self.tails.get(offset)
        if section:
            section.extend(length)
            del self.tails[offset]
        else:
            section = CodeSection(offset, length)
            self.sections.append(section)
        self.tails[offset + length] = section

    def line(self, offset, line):
        self.lines[offset] = line

    def cleanup(self):
        self.tails = None


class Z88DKList(object):
    LINE_PATTERN = re.compile("^[0-9]+\\s+([0-9A-F]+)\\s+(.+)$")
    C_LINE = re.compile("^C_LINE\\s+([0-9]+),\"([\\w.]+):?:?.*\"$")
    NEW_SYMBOL = re.compile("^\\.(\\w+)$")
    NEW_TMP_LABEL = re.compile("^\\.i_.*$")
    CODE = re.compile("^([0-9A-F\\s]+)\\s.*$")

    def __init__(self):

        self.current_symbol = None
        self.current_line = None
        self.current_file = None
        self.symbols = {}

    def parse(self, path):
        if not os.path.isdir(path):
            raise RuntimeError("Not a directory: {0}".format(path))

        lists = filter(lambda x: x.endswith(".lis"), os.listdir(path))

        for filename in lists:
            full_path = os.path.join(path, filename)

            with open(full_path, "r") as f:

                while True:
                    line = f.readline()
                    if not line:
                        break
                    m = Z88DKList.LINE_PATTERN.match(line)
                    if m:
                        offset = int(m.group(1), 16)
                        payload = m.group(2)

                        self.process_line(offset, payload)

                self.cleanup_symbol()

    def load(self, o):
        if "symbols" not in o:
            return

        self.symbols = {}
        for name, symbol in o["symbols"].items():
            s = Symbol(name)
            s.load(symbol)
            self.symbols[name] = s

    def dump(self):
        o = {}
        symbols = {}
        o["symbols"] = symbols
        for name, symbol in self.symbols.items():
            symbols[name] = symbol.dump()
        return o

    def cleanup_symbol(self):
        if self.current_symbol:
            self.current_symbol.cleanup()

    def process_line(self, offset, payload):
        if Z88DKList.NEW_TMP_LABEL.match(payload):
            # ignore labels
            return

        as_symbol = Z88DKList.NEW_SYMBOL.match(payload)
        if as_symbol:
            self.cleanup_symbol()
            symbol_name = as_symbol.group(1)
            self.current_symbol = Symbol(symbol_name)
            self.symbols[symbol_name] = self.current_symbol
            self.current_line = None
            self.current_file = None
            return

        if self.current_symbol is None:
            return

        as_line = Z88DKList.C_LINE.match(payload)
        if as_line:
            self.current_line = int(as_line.group(1))
            self.current_symbol.line(offset, self.current_line)
            if self.current_file is None:
                self.current_file = as_line.group(2)
                self.current_symbol.file_name = self.current_file
            return

        as_code = Z88DKList.CODE.match(payload)
        if as_code:
            code_hex = re.sub('\\s', '', as_code.group(1))
            code = codecs.decode(code_hex, 'hex_codec')
            length = len(code)
            self.current_symbol.code(offset, length)
            return


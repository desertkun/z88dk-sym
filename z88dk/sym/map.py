import os
import re
from collections import OrderedDict


class Z88DKAbsoluteSection(object):
    def __init__(self, sym, address, sec):
        self.sym = sym
        self.address = address
        self.sec = sec

    def matches(self, address):
        return self.address <= address < self.address + self.sec.length


class Z88DKAbsoluteSymbol(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.sections = []
        self.file_name = None
        self.lines = OrderedDict()

    def match(self, addr):
        for sec in self.sections:
            if sec.matches(addr):
                code = max(k for k in self.lines if k <= addr)
                return sec, self.lines[code]
        return None

    def enhance(self, sym):
        self.file_name = sym.file_name
        local = sym.sections[0].offset

        for offset, line in sym.lines.items():
            fixed_offset = offset - local + self.address
            self.lines[fixed_offset] = line

        for sec in sym.sections:
            address = sec.offset - local + self.address
            self.sections.append(Z88DKAbsoluteSection(self, address, sec))


class Z88DKMap(object):
    SYMBOL_PATTERN = re.compile("^([\\w]+)\\s+=\\s+\\$([A-Z0-9]+)\\s;\\s(\\w+),\\s(\\w+),\\s(\\w*),\\s(\\w+)"
                                ",\\s(\\w+),\\s([\\w.]+).*$")

    def __init__(self, path):
        self.symbols = {}

        if not os.path.isfile(path):
            raise RuntimeError("Not a file: {0}".format(path))

        with open(path, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break

                m = Z88DKMap.SYMBOL_PATTERN.match(line)
                if m:
                    symbol_name = m.group(1)
                    address = m.group(2)
                    kind = m.group(3)
                    visibility = m.group(4)
                    object_file = m.group(6)
                    src = m.group(7)
                    file_name = m.group(8)

                    self.process_line(symbol_name, address, kind, visibility, object_file, src, file_name)

    def enhance(self, lst):
        for name, sym in lst.symbols.items():
            our = self.symbols.get(name)
            if our:
                our.enhance(sym)

    def locate(self, addr):
        for name, sym in self.symbols.items():
            m = sym.match(addr)
            if m:
                return m

    def process_line(self, symbol_name, address, kind, visibility, file, src, file_name):
        if kind == "addr" and src == "code_compiler" and visibility == "public":
            decoded_addr = int(address, 16)
            self.symbols[symbol_name] = Z88DKAbsoluteSymbol(symbol_name, decoded_addr)

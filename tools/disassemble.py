import sys
import opcodes as opcodes_file


class Disassembler:
    def __init__(self, executable_path) -> None:
        self.executable_path = executable_path
        self.executable_file = None

    def read_int(self, byte_count=4):
        bts = self.executable_file.read(byte_count)
        return int.from_bytes(bts, 'little')

    def skip_zeros(self):
        if self.executable_file.tell() == self.file_size: return

        while self.executable_file.read(1) == b'\x00':
            pass
        self.executable_file.seek(-1, 1)

    def read_short(self):
        return self.read_int(2)

    def read_byte(self):
        return self.read_int(1)

    def read_literal(self):
        size = self.read_short()
        literal = self.executable_file.read(size)
        return literal

    def print_bytes(self, bts):
        for b in bts:
            print('%.2X ' % b, end='')

    def print_int(self, value, comment='', count=4, newline=True):
        print('%s ' % comment, end='')
        bts = value.to_bytes(count, 'little')
        self.print_bytes(bts)
        if newline:
            print()

    def print_short(self, value, comment=''):
        self.print_int(value, comment, count=2)

    def print_byte(self, value, comment=''):
        self.print_int(value, comment, count=1)

    def literal_is_offset(self, pointer):
        return (pointer & 0x07) == 0x07

    def read_function(self):
        function_start = self.executable_file.tell()
        function_size = self.read_short() << 3
        refs = self.read_short()
        flags = self.read_short()
        stack_limit = self.read_byte()
        argument_range_end = self.read_byte()
        register_range_end = self.read_byte()
        identifier_range_end = self.read_byte()
        const_literal_range_end = self.read_byte()
        literal_range_end = self.read_byte()
        literal_count = literal_range_end - register_range_end

        identifiers = []
        const_literals = []
        literals = []

        def append_literals(count, literal_list):
            for i in range(count):
                identifier_pointer = self.read_int()
                value = 'not offset'
                if self.literal_is_offset(identifier_pointer):
                    if (identifier_pointer & 0x8) != 0:
                        value = 'number'
                    else:
                        current_pos = self.executable_file.tell()
                        address = self.literal_table_start + (identifier_pointer >> 4)
                        self.executable_file.seek(address)
                        value = self.read_literal()
                        self.executable_file.seek(current_pos)
                else:
                    value = 'num %i' % (identifier_pointer >> 4)
                literal_list.append({
                    'address': identifier_pointer,
                    'value': value
                })

        append_literals(identifier_range_end - register_range_end, identifiers)
        append_literals(const_literal_range_end - identifier_range_end, const_literals)

        for i in range(const_literal_range_end, literal_range_end):
            literal = self.read_int()
            literals.append({
                'address': literal,
                'value': 'literal %.2X %.2X %.2X %.2X' % tuple(literal.to_bytes(4, 'little'))
            })

        code_start = self.executable_file.tell()
        header_size = code_start - function_start
        code_size = function_size - header_size
        code = self.executable_file.read(code_size)

        function = {
            'name': 'unknown',
            'start': function_start,
            'code_start': code_start,
            'size': function_size,
            'refs': refs,
            'flags': flags,
            'stack_limit': stack_limit,
            'argument_range_end': argument_range_end,
            'register_range_end': register_range_end,
            'identifier_range_end': identifier_range_end,
            'const_literal_range_end': const_literal_range_end,
            'literal_range_end': literal_range_end,
            'identifiers': identifiers,
            'const_literals': const_literals,
            'literals': literals,
            'code': code
        }

        self.executable_file.seek(function_start + function_size, 0)
        self.skip_zeros()
        return function

    def resolve_function_literals(self, functions):
        for function in functions:
            for literal in function['literals']:
                address = literal['address'] + self.function_start
                function_index = 0
                for function2 in functions:
                    if address == function2['start']:
                        literal['value'] = 'function %i' % function_index
                    function_index = function_index + 1

    def decode_code(self, function, functions, only_scan_function_names):
        code = function['code']
        opcodes = opcodes_file.opcodes
        opcodes_ext = opcodes_file.opcodes_ext
        index = 0
        if not only_scan_function_names:
            print('// disassembly')

        while index < code.__len__():
            opcode = code[index]
            opcode_data = opcodes[opcode]
            if opcode == 0:
                index = index + 1
                if index >= code.__len__():
                    return
                opcode = code[index]
                if opcode == 0x00:
                    continue # noop, mostl at end of functions (as padding i suppose)
                try:
                    opcode_data = opcodes_ext[opcode]
                except KeyError:
                    pass
            name = opcode_data['name']
            if name == 'CBC_PUSH_THREE_LITERALS':
                opcode_data['literal_args'] = 3

            literals = function['identifiers'] + function['const_literals'] + function['literals']

            if only_scan_function_names:
                if name == 'CBC_INITIALIZE_VAR':
                    referenced_func_name = literals[code[index + 1] - function['register_range_end']]['value']
                    referenced_func_address = literals[code[index + 2] - function['register_range_end']]['address'] + self.function_start
                    for function in functions:
                        if referenced_func_address == function['start']:
                            try:
                                function['name'] = referenced_func_name.decode('ascii')
                            except:
                                function['name'] = 'cannot decode'
                            break
                index = index + 1 + opcode_data['literal_args'] + opcode_data['byte_args'] + opcode_data['branch_args']
                continue

            print('%i  %.2X: %s  ' % (index, opcode, name), end='')
            opcode_index = index

            for i in range(opcode_data['literal_args']):
                index = index + 1
                identifier_index = code[index]
                print('lit %.2X ' % (identifier_index), end='')
                if identifier_index < function['argument_range_end']:
                    print('(arg %i)   ' % identifier_index, end='')
                elif identifier_index < function['register_range_end']:
                    print('(register %i)   ' % (identifier_index - function['argument_range_end']), end='')
                else:
                    print('(literal %s)   ' % (literals[identifier_index - function['register_range_end']]['value']), end='')


            for i in range(opcode_data['byte_args']):
                index = index + 1
                arg = code[index]
                print('byte(%.2X  number: %i) ' % (arg, arg + 1), end='')

            for i in range(opcode_data['branch_args']):
                index = index + 1
                try:
                    arg = code[index]
                    print('branch(%.2X  number: %i  address: %i) ' % (arg, arg, opcode_index + arg), end='')
                except:
                    print('error decoding range', file=sys.stderr)
                    pass

            print()
            index = index + 1

    def start(self):
        with open(self.executable_path, 'rb') as self.executable_file:
            self.executable_file.seek(0, 2)
            file_size = self.executable_file.tell()
            self.file_size = file_size
            self.executable_file.seek(0, 0)

            signature = self.executable_file.read(4)
            if signature != b'JRRY':
                raise Exception('file is does not start with jerry signature')
            version = self.read_int()
            if version != 0x18:
                raise Exception('file version is not supported')
            global_flags = self.read_int()
            literal_table_start = self.read_int()
            self.literal_table_start = literal_table_start
            function_count = self.read_int()
            function_start = self.read_int()
            self.function_start = function_start

            self.executable_file.seek(function_start)

            functions = []

            while self.executable_file.tell() < literal_table_start:
                functions.append(self.read_function())

            # self.resolve_function_literals(functions)

            function_index = 0
            for function in functions:
                start = function['start']
                self.executable_file.seek(start)
                if function_index == 0:
                    print('// function %i (main code)' % function_index)
                else:
                    print('// function %i  "%s"' % (function_index, function['name']))
                function_index = function_index + 1
                self.print_short(function['start'], 'start:')
                self.print_short(function['size'] >> 3, 'size:')
                self.print_short(function['refs'], 'refs:')
                self.print_short(function['flags'], 'flags:')

                self.print_byte(function['stack_limit'], 'stack depth:')
                self.print_byte(function['argument_range_end'], 'argument_range_end:')
                self.print_byte(function['register_range_end'], 'register_range_end:')
                self.print_byte(function['identifier_range_end'], 'identifier_range_end:')
                self.print_byte(function['const_literal_range_end'], 'const_literal_range_end:')
                self.print_byte(function['literal_range_end'], 'literal_range_end:')

                def print_values(header, values):
                    print(header)
                    i = 0
                    for identifier in values:
                        print(i, end='')
                        i = i + 1
                        self.print_int(identifier['address'], newline=False)
                        print(': %s' % identifier['value'])

                print_values('// identifiers', function['identifiers'])
                print_values('// const literals', function['const_literals'])
                print_values('// literals', function['literals'])
                print('// code')
                self.print_bytes(function['code'])
                print()
                self.decode_code(function, functions, True)
                self.decode_code(function, functions, False)

                print()
                print()

            pass


if __name__ == '__main__':
    disassembler = Disassembler(sys.argv[1])
    disassembler.start()

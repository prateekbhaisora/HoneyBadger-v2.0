import json
import ast
from utils import run_command
from ast_helper import AstHelper

class Source:
    def __init__(self, filename):
        self.filename = filename
        self.content = self.__load_content()
        self.line_break_positions = self.__load_line_break_positions()

    def __load_content(self):
        with open(self.filename, 'r') as f:
            content = f.read()
        return content

    def __load_line_break_positions(self):
        return [i for i, letter in enumerate(self.content) if letter == '\n']

# This class is used to manage mappings for smart contracts name and their source code, including methods for finding source code, 
# getting locations, reducing program counters, checking variable names, and converting offsets to line and column numbers. 
# It also includes class methods for loading position groups and internal methods for converting positions and character positions.
class SourceMap:
    parent_filename = ""
    position_groups = {}
    sources = {}
    ast_helper = None

    def __init__(self, cname, parent_filename):
        self.cname = cname
        # If parent filename is empty, then assign source filename to parent filename, load position groups and ast helper
        if not SourceMap.parent_filename:
            SourceMap.parent_filename = parent_filename
            # These position groups are used to map bytecode positions to source code locations
            SourceMap.position_groups = SourceMap.__load_position_groups()
            # The AstHelper instance is used to assist in parsing and analyzing the abstract syntax tree (AST) of the contract source code
            SourceMap.ast_helper = AstHelper(SourceMap.parent_filename)
        self.source = self.__get_source()
        self.positions = self.__get_positions()
        self.instr_positions = {}
        self.var_names = self.__get_var_names()
        self.func_call_names = self.__get_func_call_names()

    # This method is used to find source code given a program counter (pc)
    def find_source_code(self, pc):
        try:
            pos = self.instr_positions[pc]
        except:
            return ""
        begin = pos['begin']
        end = pos['end']
        return self.source.content[begin:end]

    # This method converts program counters (pcs) to a string representation
    def to_str(self, pcs, bug_name):
        s = ""
        for pc in pcs:
            source_code = self.find_source_code(pc).split("\n", 1)[0]
            if not source_code:
                continue

            location = self.get_location(pc)
            s += "\n%s:%s:%s\n" % (self.cname, location['begin']['line'] + 1, location['begin']['column'] + 1)
            s += source_code + "\n"
            s += "^"
        return s
    
    # This method retrieves the location of a program counter (pc) in terms of line and column numbers
    def get_location(self, pc):
        pos = self.instr_positions[pc]
        return self.__convert_offset_to_line_column(pos)
    
    # This method reduces the same position program counters (pcs) to a dictionary
    def reduce_same_position_pcs(self, pcs):
        d = {}
        for pc in pcs:
            pos = str(self.instr_positions[pc])
            if pos not in d:
                d[pos] = pc
        return d.values()

    # This method checks if a variable name is a parameter or state variable
    def is_a_parameter_or_state_variable(self, var_name):
        try:
            names = [
                node.id for node in ast.walk(ast.parse(var_name))
                if isinstance(node, ast.Name)
            ]
            if names[0] in self.var_names:
                return True
        except:
            return False
        return False

    # This method gets the source code associated with a contract
    def __get_source(self):
        fname = self.__get_filename()
        if SourceMap.sources.has_key(fname):
            return SourceMap.sources[fname]
        else:
            SourceMap.sources[fname] = Source(fname)
            return SourceMap.sources[fname]

    # This method gets variable names associated with a contract
    def __get_var_names(self):
        return SourceMap.ast_helper.extract_state_variable_names(self.cname)

    # This method gets function call names associated with a contract
    def __get_func_call_names(self):
        func_call_srcs = SourceMap.ast_helper.extract_func_call_srcs(self.cname)
        func_call_names = []
        for src in func_call_srcs:
            src = src.split(":")
            start = int(src[0])
            end = start + int(src[1])
            func_call_names.append(self.source.content[start:end])
        return func_call_names

    @classmethod
    # This class method loads position groups for contracts using solc (Solidity compiler).
    def __load_position_groups(cls):
        # Tells solc to output the compiler output in the form of a JSON object with the assembly (asm) field included.
        cmd = "solc --combined-json asm %s" % cls.parent_filename
        out = run_command(cmd)
        # This line parses the JSON-formatted output (out) obtained from executing the above command. 
        # It converts the JSON string into a Python dictionary using the json.loads() function.
        out = json.loads(out)
        # This value is expected to be a dictionary containing information about the contracts compiled by solc, including their positions in the bytecode.
        return out['contracts']

    # This method gets positions of instructions for a contract
    def __get_positions(self):
        asm = SourceMap.position_groups[self.cname]['asm']['.data']['0']
        positions = asm['.code']
        while(True):
            try:
                positions.append(None)
                positions += asm['.data']['0']['.code']
                asm = asm['.data']['0']
            except:
                break
        return positions

    # This method converts offsets to line and column numbers
    def __convert_offset_to_line_column(self, pos):
        ret = {}
        ret['begin'] = None
        ret['end'] = None
        if pos['begin'] >= 0 and (pos['end'] - pos['begin'] + 1) >= 0:
            ret['begin'] = self.__convert_from_char_pos(pos['begin'])
            ret['end'] = self.__convert_from_char_pos(pos['end'])
        return ret

    # This method converts from character position to line and column numbers
    def __convert_from_char_pos(self, pos):
        line = self.__find_lower_bound(pos, self.source.line_break_positions)
        if self.source.line_break_positions[line] != pos:
            line += 1
        begin_col = 0 if line == 0 else self.source.line_break_positions[line - 1] + 1
        col = pos - begin_col
        return {'line': line, 'column': col}

    # This method finds the lower bound of a target value in a sorted array
    def __find_lower_bound(self, target, array):
        start = 0
        length = len(array)
        while length > 0:
            half = length >> 1
            middle = start + half
            if array[middle] <= target:
                length = length - 1 - half
                start = middle + 1
            else:
                length = half
        return start - 1

    # This method gets the filename associated with a contract
    def __get_filename(self):
        return self.cname.split(":")[0]

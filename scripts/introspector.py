import pycparser
import jsonschema
import json
import sys
import os
import re
import tempfile
import csv
from subprocess import check_output, CalledProcessError
from argparse import ArgumentParser

ASTNode = pycparser.c_parser.c_ast.Node

config_schema = {
    "type": "object",
    "required": [
        "ignoreCapabilities",
        "namespaces",
        "preprocessor"
    ],
    "additionalProperties": False,
    "properties": {
        "ignoreCapabilities": {
            "type": "array",
            "items": { "type": "string" },
            "uniqueItems": True
        },
        "namespaces": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string" }
        },
        "preprocessor": {
            "type": "object",
            "additionalProperties" : False,
            "required": [
                "executable",
                "arguments",
                "replaceBeforePreprocessing",
                "replaceAfterPreprocessing"
            ],
            "properties": {
                "executable": { "type": "string", "minLength": 1 },
                "arguments": {
                    "type": "array",
                    "items": { "type": "string", "minLength": 1 },
                    "uniqueItems": True
                },
                "replaceBeforePreprocessing" : {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": { "type": "string" },
                        "minItems": 2,
                        "maxItems": 2
                    }
                },
                "replaceAfterPreprocessing" : {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": { "type": "string" },
                        "minItems": 2,
                        "maxItems": 2
                    }
                }
            }
        }
    }
}

config: dict = {}

def is_capability_ignored(capability: str) -> bool:
    namespace_hits = 0
    for namespace in config['namespaces']:
        if capability.startswith(namespace):
            namespace_hits = namespace_hits + 1

    if namespace_hits == 0:
        return True

    for pattern in config['ignoreCapabilities']:
        if re.search(pattern, capability):
            return True

    return False

class CapabilitiesVisitor(pycparser.c_parser.c_ast.NodeVisitor):
    _nodes_stack: list[ASTNode]

    capabilities: list[tuple[str, str]]

    def __init__(self):
        self._nodes_stack = []
        self.capabilities = []
        self.count = 0

    def _create_capability_name(self, type_hierarchy: str, offset: int = 0) -> str:
        if type_hierarchy.endswith("Decl.TypeDecl."):
            type_hierarchy = type_hierarchy.removesuffix("Decl.TypeDecl.")
            name = getattr(self._nodes_stack[-1 - offset], 'name', getattr(self._nodes_stack[-2], 'name'))
            return self._create_capability_name(type_hierarchy, offset + 2) + name

        if type_hierarchy.endswith("Decl.FuncDecl."):
            type_hierarchy = type_hierarchy.removesuffix("Decl.FuncDecl.")
            name = getattr(self._nodes_stack[-2 - offset], 'name')
            return self._create_capability_name(type_hierarchy, offset + 2) + name + "()"

        if type_hierarchy.endswith("Decl.TypeDecl.Struct."):
            type_hierarchy = type_hierarchy.removesuffix("Decl.TypeDecl.Struct.")
            name = getattr(self._nodes_stack[-3 - offset], 'name')
            return self._create_capability_name(type_hierarchy, offset + 3) + name + "."

        if type_hierarchy.endswith("Decl.TypeDecl.Union."):
            type_hierarchy = type_hierarchy.removesuffix("Decl.TypeDecl.Union.")
            name = getattr(self._nodes_stack[-3 - offset], 'name')
            return self._create_capability_name(type_hierarchy, offset + 3) + name + "."

        if type_hierarchy.endswith("TypeDecl.Struct."):
            type_hierarchy = type_hierarchy.removesuffix("TypeDecl.Struct.")
            return self._create_capability_name(type_hierarchy, offset + 2) + "."

        if type_hierarchy.endswith("TypeDecl.Union."):
            type_hierarchy = type_hierarchy.removesuffix("TypeDecl.Union.")
            return self._create_capability_name(type_hierarchy, offset + 2) + "."

        if type_hierarchy.endswith("TypeDecl.Enum."):
            type_hierarchy = type_hierarchy.removesuffix("TypeDecl.Enum.")
            return self._create_capability_name(type_hierarchy, offset + 2) + "::"

        if type_hierarchy.endswith("Enumerator."):
            type_hierarchy = type_hierarchy.removesuffix("Enumerator.")
            name = getattr(self._nodes_stack[-1 - offset], 'name')
            return self._create_capability_name(type_hierarchy, offset + 1) + name

        if type_hierarchy.endswith("Typedef."):
            type_hierarchy = type_hierarchy.removesuffix("Typedef.")
            name = getattr(self._nodes_stack[-1 - offset], 'name')
            return self._create_capability_name(type_hierarchy, offset + 1) + name

        return ""

    def _add_capability(self):
        type_hierarchy = ""

        for node in self._nodes_stack:
            type_hierarchy += node.__class__.__name__
            type_hierarchy += "."

        capability_name = self._create_capability_name(type_hierarchy)

        if capability_name and not capability_name.endswith(('.', '::')) and not is_capability_ignored(capability_name):
            self.capabilities.append((capability_name, str(self._nodes_stack[-1].coord)))

        self.count = self.count + 1

        self._nodes_stack.pop()

    def visit_Typedef(self, node: ASTNode):
        if not getattr(node, 'name').startswith(config['namespaces'][0]):
            return

        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()

    def visit_Decl(self, node: ASTNode):
        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()

    def visit_Struct(self, node: ASTNode):
        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()

    def visit_Enum(self, node: ASTNode):
        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()

    def visit_Union(self, node: ASTNode):
        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()

    def visit_Enumerator(self, node: ASTNode):
        self._nodes_stack.append(node)
        self._add_capability()

    def visit_FuncDecl(self, node: ASTNode):
        self._nodes_stack.append(node)
        self._add_capability()

    def visit_FuncDef(self, node: ASTNode):
        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()

    def visit_TypeDecl(self, node: ASTNode):
        self._nodes_stack.append(node)
        self.generic_visit(node)
        self._add_capability()


def load_config(config_path: str) -> None:
    global config

    try:
        config_file = open(config_path)
    except OSError:
        print("Cannot open config file '", config_path, "'. Either access is restricted or it does not exist", file=sys.stderr)
        exit(-1)

    try:
        config = json.load(config_file)
    except json.JSONDecodeError as e:
        print("Config file '", config_path, "' has JSON syntax errors at line", '%d:%d' % (e.lineno, e.colno), file=sys.stderr)
        print(e.msg, file=sys.stderr)
        exit(-1)
    except UnicodeDecodeError:
        print("Config file '", config_path, "' is not encoded in UTF-8 format", file=sys.stderr)
        exit(-1)

    try:
        jsonschema.validate(instance=config, schema=config_schema)
    except jsonschema.ValidationError as e:
        print("Config file '", config_path, "' is mis-configured:", file=sys.stderr)
        print(e.message, file=sys.stderr)
        exit(-1)

def apply_preprocessing(source_code: list[str], output_dir: str) -> None:
    print("Preprocessing's working directory is:", os.getcwd(), ". Keep this in mind if you are using relative include paths in the configuration.")
    print()

    for code_file in source_code:
        preprocessed_code = ""

        with open(code_file, 'r') as file:
            preprocessed_code = file.read()

        path_list = [config['preprocessor']['executable']]
        path_list += config['preprocessor']['arguments']
        path_list += ['-pipe']

        for [reg, sub] in config['preprocessor']['replaceBeforePreprocessing']:
            preprocessed_code = re.sub(reg, sub, preprocessed_code)

        try:
            preprocessed_code = check_output(path_list, universal_newlines=True, input=preprocessed_code)
        except CalledProcessError as e:
            print("Preprocessor could not complete its job ( err code", e.returncode, "). This may be because of insufficient include paths.", file=sys.stderr)
            exit(-1)

        for [reg, sub] in config['preprocessor']['replaceAfterPreprocessing']:
            preprocessed_code = re.sub(reg, sub, preprocessed_code)

        preprocessed_code = re.sub('<stdin>', code_file, preprocessed_code)

        with open(os.path.join(output_dir, os.path.basename(code_file)), 'w') as file:
            file.write(preprocessed_code)

def parse_capabilites(preprocessed_code_dir: str, ast_dump_path: str|None) -> list[tuple[str, str]]:
    capabilities: list[tuple[str, str]] = []

    files_list = os.listdir(preprocessed_code_dir)

    if ast_dump_path:
        with open(ast_dump_path, 'a') as dump: #lol
            dump.truncate(0)

    for code_file in files_list:
        if os.path.isdir(code_file):
            continue

        code_file_path = os.path.join(preprocessed_code_dir, code_file)

        ast: pycparser.c_parser.c_ast.FileAST

        try:
            ast = pycparser.parse_file(code_file_path)
        except pycparser.c_parser.ParseError as e:
            print("Unable to parse source code. Changes to the introspector's configuration is needed.", file=sys.stderr)
            print("Problematic file:", code_file_path + ": ", file=sys.stderr)
            print("    ", ' '.join(e.args), file=sys.stderr)
            exit(-1)

        nodes_visitor = CapabilitiesVisitor()
        nodes_visitor.visit(ast)
        capabilities += nodes_visitor.capabilities

        if ast_dump_path:
            with open(ast_dump_path, 'a') as dump:
                print(code_file_path, ':', sep='', end='', file=dump)
                ast.show(buf=dump)
                print(file=dump)

    return capabilities

def write_capabilites_csv(capabilities: list[tuple[str, str]], csv_file_path: str) -> None:
    field_names = ['Capability', 'Coord']
    with open(csv_file_path, 'w') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(field_names)
        csv_writer.writerows(capabilities)

def main():
    parser = ArgumentParser(description="Scan clay's source code for relevant public API constructs and output its capabilities as a csv")
    parser.add_argument('source_code', type=str, nargs='+', help="Clay's source code files to introspect")
    parser.add_argument('-c', '--config', type=str, required=True, help="File path to the JSON config file")
    parser.add_argument('-o', '--output', type=str, required=True, help="Output file path to write Clay's capabilities to")
    parser.add_argument('-p', '--preprocessor-output', type=str, help="Output directory of the source code after it was preprocessed for debugging purposes")
    parser.add_argument('-s', '--skip-preprocessing', action='store_true', help="Skip preprocessing for debugging purposes")
    parser.add_argument('-d', '--dump-ast', type=str, help="Output file to dump the AST into for debugging purposes")
    args = parser.parse_args()

    temp_dir: tempfile.TemporaryDirectory|None = None

    if args.preprocessor_output:
        preprocessed_source_code_dir = args.preprocessor_output
        os.makedirs(preprocessed_source_code_dir, exist_ok=True)
    else:
        temp_dir = tempfile.TemporaryDirectory()
        preprocessed_source_code_dir = temp_dir.name

    exit_code = 0
    load_config(args.config)

    try:
        if not args.skip_preprocessing:
            apply_preprocessing(args.source_code, preprocessed_source_code_dir)
        ast_dump_path: str|None = None
        if args.dump_ast:
            ast_dump_path = args.dump_ast
        capabilites = parse_capabilites(preprocessed_source_code_dir, ast_dump_path)
        write_capabilites_csv(capabilites, args.output)
    except FileNotFoundError as e:
        print("Source code or generic file '", e.filename, "' does not exist", file=sys.stderr)
        exit_code = -1
    finally:
        if temp_dir:
            temp_dir.cleanup()

    exit(exit_code)

if __name__ == "__main__":
    main()

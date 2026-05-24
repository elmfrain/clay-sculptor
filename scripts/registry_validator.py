import sys
import json
import jsonschema
from argparse import ArgumentParser

css_property_expansion_methods = [
    "clockwise4"
]

enum_value = {
    "type": "object",
    "required": [ "enum", "value" ],
    "additionalProperties": False,
    "properties": {
        "enum": { "type": "string", "minLength": 1 },
        "value": { "type": "string", "minLength": 1 }
    }
}

css_enum_value_bindings = {
    "type": "object",
    "additionalProperties": { "type": "string", "minLength": 1 }
}

struct_member_assignment = {
    "type": "object",
    "required": [ "member", "value" ],
    "additionalProperties": False,
    "properties": {
        "member": { "type": "string", "minLength": 1 },
        "value": {
            "oneOf": [
                { "type": "string", "minLength": 1 },
                { "$ref": "#/definitions/structDeclaration" },
                enum_value
            ]
        }
    }
}

struct_declaration = {
    "type": "object",
    "required": [ "struct" ],
    "additionalProperties": False,
    "properties": {
        "struct": { "type": "string", "minLength": 1 },
        "assign": {
            "oneOf": [
                struct_member_assignment,
                {
                    "type": "array",
                    "items": struct_member_assignment
                }
            ]
        }
    }
}

css_property = {
    "type": "object",
    "required": [ "syntax" ],
    "additionalProperties": False,
    "properties": {
        "syntax": { "type": "string", "minLength": 1 },
        "isShorthand": { "type": "boolean", "default": False },
        "expandsTo": {
            "type": "array",
            "items": { "type": "string", "minLength": 1 },
            "uniqueItems": True
        },
        "expansionMethod": {
            "type": "string",
            "enum": css_property_expansion_methods
        },
        "enumValues": css_enum_value_bindings,
        "lowersTo": struct_declaration
    }
}

xml_attribute = {
    "type": "object",
    "required": [ "syntax" ],
    "additionalProperties": False,
    "properties": {
        "syntax": { "type": "string", "minLength": 1 },
        "lowersTo": struct_declaration
    }
}

css_properties = {
    "type": "object",
    "additionalProperties": css_property
}

xml_attributes = {
    "type": "object",
    "additionalProperties": xml_attribute
}

capability = {
    "type": "object",
    "required": [
        "capability",
        "domain"
    ],
    "additionalProperties": False,
    "properties": {
        "capability": { "type": "string", "minLength": 1 },
        "domain": { "type": "string", "minLength": 1 },
        "implements": {
            "type": "array",
            "items": { "type": "string", "minLength": 1 },
            "uniqueItems": True
        },
        "authoring": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cssProperties": css_properties,
                "xmlAttributes": xml_attributes
            }
        }
    }
}

registry_schema = {
    "definitions": {
        "structDeclaration": struct_declaration
    },
    "type": "array",
    "items": capability
}

def load_registry(registry_path: str):
    try:
        registry_file = open(registry_path)
    except OSError:
        print("Cannot open registry file '", registry_path, "' Either access is restricted or it does not exist", file=sys.stderr)
        exit(-1)

    try:
        registry = json.load(registry_file)
    except json.JSONDecodeError as e:
        print("Registry file '", registry_path, "' has JSON syntax errors at line", '%d:%d' % (e.lineno, e.colno), file=sys.stderr)
        print(e.msg, file=sys.stderr)
        exit(-1)
    except UnicodeDecodeError:
        print("Registry file '", registry_path, "' is not encoded in UTF-8 format", file=sys.stderr)
        exit(-1)
    finally:
        registry_file.close()

    try:
        jsonschema.validate(instance=registry, schema=registry_schema)
    except jsonschema.ValidationError as e:
        print("Registry file '", registry_path, "' does not follow schema:", file=sys.stderr)
        print(e.absolute_schema_path, e.message, file=sys.stderr)
        exit(-1)

def main():
    parser = ArgumentParser(description="Validate a capability registry JSON file to check if it follows the schema and if it semantically sound")
    parser.add_argument('-r', '--registry', type=str, required=True, help="JSON capability registry to validate")
    parser.add_argument('-c', '--capabilities', type=str, required=True, help="CSV file listing Clay's capabilities")
    args = parser.parse_args()

    load_registry(args.registry)

if __name__ == "__main__":
    main()

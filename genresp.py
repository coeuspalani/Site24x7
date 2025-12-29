import argparse
import yaml
import json
import sys


def load_yaml(file):
    with open(file, "r") as f:
        return yaml.safe_load(f)



def generate_example(schema):
    if not schema:
        return None

    schema_type = schema.get("type")

    if schema_type == "object":
        result = {}
        for prop, prop_schema in schema.get("properties", {}).items():
            result[prop] = generate_example(prop_schema)
        return result

    if schema_type == "array":
        item_schema = schema.get("items", {})
        return [
            generate_example(item_schema),
            generate_example(item_schema)
        ]

    if schema_type == "string":
        return schema.get("default", "string_example")

    if schema_type == "integer":
        return schema.get("default", 1)

    if schema_type == "number":
        return schema.get("default", 1.0)

    if schema_type == "boolean":
        return schema.get("default", True)

    
    return None

def get_response_schema(openapi, path, method, status):
    try:
        return (
            openapi["paths"][path][method]["responses"][status]
            ["content"]["application/json"]["schema"]
        )
    except KeyError:
        raise ValueError(
            f"Schema not found for {method.upper()} {path} ({status})"
        )


def main(yaml_file, path, method, status="200", output=None):

    openapi = load_yaml(yaml_file)
    schema = get_response_schema(
        openapi,
        path,
        method.lower(),
        status
    )

    sample_response = generate_example(schema)

    if output:
        with open(output, "w") as f:
            json.dump(sample_response, f, indent=2)
        print(f"Sample response written to {output}")
 
    print("\n--- SAMPLE API RESPONSE ---\n")
    return sample_response


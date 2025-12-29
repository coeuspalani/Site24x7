import argparse
import xml.etree.ElementTree as ET
import yaml
import os
import sys


def load_yaml(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_yaml(data, file):
    with open(file, "w") as f:
        yaml.dump(data, f, sort_keys=False)



def parse_all_templates_from_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    jsontemplates_node = root.find("jsontemplates")
    if jsontemplates_node is None:
        raise ValueError("Invalid XML: <jsontemplates> not found")

    templates = {}

    for tpl in jsontemplates_node.findall("jsontemplate"):
        name = tpl.attrib.get("name")
        if not name:
            continue

        entries = []

        # <key .../>
        for key in tpl.findall("key"):
            entries.append(extract_key_metadata(key))

        # <value .../>
        value = tpl.find("value")
        if value is not None:
            entries.append({
                "__kind__": "value",
                "type": value.attrib.get("type", "String"),
                "template": value.attrib.get("template"),
                "raw": dict(value.attrib),
            })

        templates[name] = entries

    return templates



def extract_key_metadata(key):
    attrs = dict(key.attrib)
    return {
        "__kind__": "key",
        "name": attrs.get("name"),
        "type": attrs.get("type", "String"),
        "template": attrs.get("template"),
        "regex": attrs.get("regex"),
        "max_len": attrs.get("max-len"),
        "min_len": attrs.get("min-len"),
        "array_size": attrs.get("array-size"),
        "required": attrs.get("required") == "true",
        "default": attrs.get("default"),
        "description": attrs.get("description"),
        "raw": attrs,
    }



def base_type_mapping(t):
    if t == "String":
        return {"type": "string"}
    if t == "long":
        return {"type": "integer", "format": "int64"}
    if t == "double":
        return {"type": "number", "format": "double"}
    if t == "boolean":
        return {"type": "boolean"}
    return {"type": "string"}



def apply_constraints(schema, meta):
    if meta.get("regex"):
        schema["pattern"] = meta["regex"]

    if meta.get("max_len"):
        schema["maxLength"] = int(meta["max_len"])

    if meta.get("min_len"):
        schema["minLength"] = int(meta["min_len"])

    if meta.get("array_size"):
        a, b = meta["array_size"].split("-")
        schema["minItems"] = int(a)
        schema["maxItems"] = int(b)

    if meta.get("default") is not None:
        schema["default"] = meta["default"]

    if meta.get("description"):
        schema["description"] = meta["description"]



def build_property_schema(meta, templates):
    t = meta["type"]

    if t == "JSONObject":
        if meta.get("template"):
            return build_schema(meta["template"], templates)
        return {"type": "object"}

    if t == "JSONArray":
        schema = {"type": "array"}

        tpl = meta.get("template")
        if tpl and tpl in templates:
            items_schema = build_schema(tpl, templates)
            schema["items"] = items_schema
        else:
            schema["items"] = {"type": "string"}

        apply_constraints(schema, meta)
        return schema

    schema = base_type_mapping(t)
    apply_constraints(schema, meta)
    return schema



def build_schema(template_name, templates):
    if template_name not in templates:
        raise ValueError(
            f"Template '{template_name}' not found. "
        )

    entries = templates[template_name]

    if len(entries) == 1 and entries[0]["__kind__"] == "value":
        v = entries[0]

        if v["type"] == "JSONObject" and v.get("template"):
            return build_schema(v["template"], templates)

        if v["type"] == "JSONArray" and v.get("template"):
            return {
                "type": "array",
                "items": build_schema(v["template"], templates)
            }

        return base_type_mapping(v["type"])


    schema = {
        "type": "object",
        "properties": {}
    }

    required = []

    for meta in entries:
        if meta["__kind__"] != "key":
            continue

        prop_schema = build_property_schema(meta, templates)
        schema["properties"][meta["name"]] = prop_schema

        if meta.get("required"):
            required.append(meta["name"])

    if required:
        schema["required"] = required

    return schema

def append_api_path(
    yaml_file,
    path,
    method,
    tag,
    summary,
    operation_id,
    schema
):
    data = load_yaml(yaml_file)

    data.setdefault("paths", {})
    data["paths"].setdefault(path, {})

    data["paths"][path][method] = {
        "tags": [tag],
        "summary": summary,
        "operationId": operation_id,
        "responses": {
            "200": {
                "description": "OK",
                "content": {
                    "application/json": {
                        "schema": schema
                    }
                }
            }
        }
    }
    save_yaml(data, yaml_file)
    return data


def main(path,method,tag,summary,operation_id,root_template,xml_file,output):

    templates = parse_all_templates_from_file(xml_file)

    schema = build_schema(root_template, templates)

    data = append_api_path(
        yaml_file=output,
        path=path,
        method=method.lower(),
        tag=tag,
        summary=summary,
        operation_id=operation_id,
        schema=schema
    )

    print("OpenAPI YAML generated successfully")
    return data



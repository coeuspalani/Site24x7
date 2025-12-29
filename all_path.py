from yamlcon import (
    parse_all_templates_from_file,
    build_schema,
    append_api_path
)
import re

XML_FILE = "xmlcon.xml"
OUTPUT_YAML = "openapi.yaml"

TAG = "auto"
SUMMARY_PREFIX = "Auto generated"


def extract_api_meta_from_xml(xml_file):
    apis = []
    current = None

    with open(xml_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("<!--") and "path:" in line and "method:" in line:
                path_match = re.search(r"path:\s*([^\s]+)", line)
                method_match = re.search(r"method:\s*([A-Z,]+)", line)

                if path_match and method_match:
                    methods = [
                        m.strip().lower()
                        for m in method_match.group(1).split(",")
                    ]

                    current = {
                        "path": path_match.group(1),
                        "methods": methods
                    }

            elif line.startswith("<jsontemplate") and current:
                name_match = re.search(r'name="([^"]+)"', line)
                if name_match:
                    current["template"] = name_match.group(1)
                    apis.append(current)
                    current = None

    return apis


def main():
    templates = parse_all_templates_from_file(XML_FILE)
    api_meta = extract_api_meta_from_xml(XML_FILE)

    count = 0

    for api in api_meta:
        schema = build_schema(api["template"], templates)

        for method in api["methods"]:
            append_api_path(
                yaml_file=OUTPUT_YAML,
                path=api["path"],
                method=method,
                tag=TAG,
                summary=f"{SUMMARY_PREFIX} {api['template']}",
                operation_id=f"{api['template']}_{method}",
                schema=schema
            )
            count += 1
            print(f"Added {method.upper()} {api['path']}")

    print(f"Converted {count} API operations into {OUTPUT_YAML}")


if __name__ == "__main__":
    main()

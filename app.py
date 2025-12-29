import flask
from flask import Flask, jsonify, request , render_template
from yamlcon import main as yaml_con
from genresp import main as gen_resp , load_yaml
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('terminal.html')


@app.route('/convert', methods=['POST'])
def convert_yaml():
    data = request.json
    path = data.get('path')
    method = data.get('method')
    tag = data.get('tag')
    summary = data.get('summary')
    operation_id = data.get('operation_id')
    root_template = data.get('root_template')
    xml_file = data.get('xml_file')
    output = data.get('output')

    yaml_con(
        path,
        method,
        tag,
        summary,
        operation_id,
        root_template,
        xml_file,
        output
    )

    return jsonify({"message": "OpenAPI YAML generated successfully"}), 200
@app.route("/available-paths", methods=["GET"])
def available_paths():
    yaml_file = "openapi.yaml"

    if not os.path.exists(yaml_file):
        return jsonify([])

    data = load_yaml(yaml_file)
    paths = data.get("paths", {})

    result = []

    for path, methods in paths.items():
        for method in methods.keys():
            result.append({
                "path": path,
                "method": method.upper()
            })

    return jsonify(result)


@app.route("/sample-response", methods=["POST"])
def sample_response():
    data = request.json

    try:
        sample = gen_resp(
            yaml_file="openapi.yaml",
            path=data["path"],
            method=data["method"]
        )
        return jsonify(sample)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)

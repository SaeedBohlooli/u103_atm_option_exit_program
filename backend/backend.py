from flask import Flask, request, jsonify
import json


PARAMS_FILE = "../shared/params.json"

app = Flask(__name__)

@app.route("/api/update_params", methods=["POST"])
def update_params():
    data = request.get_json(force=True)
    with open(PARAMS_FILE, "w") as f:
        json.dump(data, f)
    return jsonify({"status": "parameters updated", "data": data})


if __name__ == "__main__":
    # Run Flask app on port 5103
    app.run(debug=True, host="0.0.0.0", port=5103)

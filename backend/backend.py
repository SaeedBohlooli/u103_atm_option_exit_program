from flask import Flask, request, jsonify
import json


PARAMS_FILE = "../shared/params.json"

app = Flask(__name__)

@app.route("/api/set-atm-exit", methods=["POST"])
def straddle():
    # Parse JSON input
    data = request.get_json(force=True)

    # Validate required keys
    required = {"baseAtmStraddle", "contracts", "multiplier", "strike"}
    if not required.issubset(data):
        return jsonify({"error": f"Missing keys. Expected {sorted(required)}"}), 400

    # Parse and validate numeric fields
    try:
        base = float(data["baseAtmStraddle"])
        contracts = int(data["contracts"])
        multiplier = float(data["multiplier"])
        strike = float(data["strike"])
    except (ValueError, TypeError):
        return jsonify({"error": "All numeric fields must be valid numbers"}), 400

    # Example calculation (you can replace this with your own logic)
    total_value = base * contracts * multiplier * strike

    # Return JSON response
    return jsonify({
        "baseAtmStraddle": base,
        "contracts": contracts,
        "multiplier": multiplier,
        "strike": strike,
        "totalValue": total_value
    })


@app.route("/api/update_params", methods=["POST"])
def update_params():
    data = request.get_json(force=True)
    with open(PARAMS_FILE, "w") as f:
        json.dump(data, f)
    return jsonify({"status": "parameters updated", "data": data})


if __name__ == "__main__":
    # Run Flask app on port 5103
    app.run(debug=True, host="0.0.0.0", port=5103)

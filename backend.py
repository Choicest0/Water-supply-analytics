import random
import time
from flask import Flask, jsonify

app = Flask(__name__)

SECTORS = ["Dehradun-North", "Dehradun-Sahaspur", "Dehradun-Vikasnagar", "Mussoorie-Suburbs"]
SCENARIOS = ["pristine", "pristine", "heavy_runoff", "chemical_shift"]

def evaluate_safety(ph: float, tds: int, turbidity: float) -> tuple[str, str]:
    if tds > 600 or turbidity > 5.0:
        return "CRITICAL", "HALT MAIN LINE PIPELINE! Route sample splits immediately to laboratory."
    elif ph < 6.5 or ph > 8.5 or tds > 500:
        return "WARNING", "Issue Boil Water Notice. Initiate minor tank filtration check."
    return "SAFE", "Parameters regular. No immediate localized intervention required."

@app.route("/api/telemetry", methods=["GET"])
def get_telemetry():
    """Endpoint generating telemetry batch readings."""
    records = []
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    for _ in range(10):
        sector = random.choice(SECTORS)
        scenario = random.choice(SCENARIOS)

        if scenario == "pristine":
            ph = round(random.uniform(7.0, 7.6), 2)
            tds = int(random.uniform(150, 300))
            turbidity = round(random.uniform(0.8, 2.0), 2)
        elif scenario == "heavy_runoff":
            ph = round(random.uniform(6.6, 7.2), 2)
            tds = int(random.uniform(520, 680))
            turbidity = round(random.uniform(5.5, 9.8), 2)
        else:
            ph = round(random.uniform(8.7, 9.4), 2)
            tds = int(random.uniform(320, 480))
            turbidity = round(random.uniform(1.5, 4.0), 2)

        status, directive = evaluate_safety(ph, tds, turbidity)

        records.append({
            "Timestamp": current_time,
            "Sector_ID": sector,
            "pH_Level": ph,
            "TDS_PPM": tds,
            "Turbidity_NTU": turbidity,
            "Safety_Status": status,
            "Field_Directive": directive
        })

    return jsonify({"status": "success", "data": records})

if __name__ == "__main__":
    print("🚀 Starting Flask Backend Server on http://127.0.0.1:5000...")
    app.run(host="127.0.0.1", port=5000, debug=True)

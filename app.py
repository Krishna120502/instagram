
from flask import Flask, request, jsonify, send_from_directory
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os
import os
import traceback

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "submissions.xlsx")


def create_excel():
    if not os.path.exists(EXCEL_FILE):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Records"

        sheet.append([
            "Submission Time",
            "Demo Identifier",
            "Your Name"
        ])

        workbook.save(EXCEL_FILE)
        workbook.close()


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def javascript():
    return send_from_directory(BASE_DIR, "script.js")


@app.route("/results.html")
def results():
    return send_from_directory(BASE_DIR, "results.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "assets"),
        filename
    )


@app.route("/submit", methods=["POST"])
def submit():

    data = request.get_json(silent=True) or {}

    print("Received demo data:", data)

    identifier = data.get("identifier", "").strip()
    your_name = data.get("your_name", "").strip()

    if not identifier or not your_name:
        return jsonify({
            "message": "Please fill in all fields."
        }), 400

    try:
        create_excel()

        workbook = load_workbook(EXCEL_FILE)

        try:
            sheet = workbook["Records"]

            sheet.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                identifier,
                your_name
            ])

            workbook.save(EXCEL_FILE)

        finally:
            workbook.close()

        print("Demo data saved successfully!")
        print("Excel location:", EXCEL_FILE)

        return jsonify({
            "message": "Demo submission saved successfully!"
        }), 200

    except Exception:
        print("========== EXCEL ERROR ==========")
        traceback.print_exc()
        print("=================================")

        return jsonify({
            "message": "Unable to save demo submission. Check the terminal."
        }), 500


if __name__ == "__main__":
    create_excel()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

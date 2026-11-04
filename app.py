
from flask import Flask, request, jsonify, send_from_directory
import os
import psycopg

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg.connect(DATABASE_URL)


def create_table():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS demo_submissions (
                    id BIGSERIAL PRIMARY KEY,
                    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    demo_identifier VARCHAR(60) NOT NULL,
                    demo_name VARCHAR(60) NOT NULL
                )
            """)

            # Rename the old columns if the previous table already exists.
            cursor.execute("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'demo_submissions'
                        AND column_name = 'demo_code'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'demo_submissions'
                        AND column_name = 'demo_identifier'
                    ) THEN
                        ALTER TABLE demo_submissions
                        RENAME COLUMN demo_code TO demo_identifier;
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'demo_submissions'
                        AND column_name = 'demo_label'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'demo_submissions'
                        AND column_name = 'demo_name'
                    ) THEN
                        ALTER TABLE demo_submissions
                        RENAME COLUMN demo_label TO demo_name;
                    END IF;
                END $$;
            """)


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
        os.path.join(BASE_DIR, "assets"), filename
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True) or {}

    # Accept only invented demo values, never passwords or real personal data.
    demo_identifier = data.get("identifier")
    demo_name = data.get("your_name")

    if not isinstance(demo_identifier, str) or not isinstance(demo_name, str):
        return jsonify({"message": "Please enter both demo values."}), 400

    demo_identifier = demo_identifier.strip()
    demo_name = demo_name.strip()

    if not demo_identifier or not demo_name:
        return jsonify({"message": "Please enter both demo values."}), 400

    if len(demo_identifier) > 60 or len(demo_name) > 60:
        return jsonify({"message": "Each value must be 60 characters or fewer."}), 400

    try:
        create_table()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO demo_submissions
                    (demo_identifier, demo_name)
                    VALUES (%s, %s)
                    """,
                    (demo_identifier, demo_name)
                )

        return jsonify({"message": "Demo data saved successfully!"}), 200

    except Exception:
        app.logger.exception("Database submission failed")
        return jsonify({"message": "Unable to save demo data."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

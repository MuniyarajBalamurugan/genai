from flask import Flask, request, render_template
import os
import psycopg2

app = Flask(__name__)

# Upload folders
CIRCULAR_FOLDER = 'static/circulars'
PROOF_FOLDER = 'static/proofs'

os.makedirs(CIRCULAR_FOLDER, exist_ok=True)
os.makedirs(PROOF_FOLDER, exist_ok=True)

# Database connection settings
DB_HOST = "localhost"
DB_NAME = "test"
DB_USER = "postgres"
DB_PASSWORD = "1234"

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    # Get form data
    event_name = request.form["eve"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    organizer = request.form["organizer"]
    chief_guest = request.form["chief_guest"]

    # Get and save files
    circular_image = request.files["circular_image"]
    proof1 = request.files["proof1"]
    proof2 = request.files["proof2"]

    circular_path = os.path.join(CIRCULAR_FOLDER, circular_image.filename)
    proof1_path = os.path.join(PROOF_FOLDER, proof1.filename)
    proof2_path = os.path.join(PROOF_FOLDER, proof2.filename)

    circular_image.save(circular_path)
    proof1.save(proof1_path)
    proof2.save(proof2_path)

    # Insert into database
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (event_name, start_date, end_date, organizer, chief_guest, circular_path, proof1_path, proof2_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (event_name, start_date, end_date, organizer, chief_guest, circular_path, proof1_path, proof2_path))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return f"Database error: {e}"

    return f"Event '{event_name}' has been submitted and saved successfully!"

if __name__ == "__main__":
    app.run(debug=True)

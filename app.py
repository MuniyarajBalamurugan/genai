from flask import Flask, request, render_template
import os
import psycopg2

app = Flask(__name__)

# Use DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL)

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

    # Get uploaded files
    circular_image = request.files["circular_image"]
    proof1 = request.files["proof1"]
    proof2 = request.files["proof2"]

    # Read file contents as binary
    circular_data = circular_image.read()
    proof1_data = proof1.read()
    proof2_data = proof2.read()

    # Insert into database
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events 
            (event_name, start_date, end_date, organizer, chief_guest, circular, proof1, proof2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (event_name, start_date, end_date, organizer, chief_guest, circular_data, proof1_data, proof2_data))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return f"Database error: {e}"

    return f"Event '{event_name}' has been submitted and saved successfully!"

if __name__ == "__main__":
    app.run(debug=True)

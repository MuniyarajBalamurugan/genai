from flask import Flask, request, render_template, jsonify
import os
import psycopg2

app = Flask(__name__)

# Use DATABASE_URL from environment (Render provides this)
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

    # Get and read files as binary
    circular_image = request.files["circular_image"].read()
    proof1 = request.files["proof1"].read()
    proof2 = request.files["proof2"].read()

    # Insert into database
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (
                event_name, start_date, end_date, 
                organizer, chief_guest, 
                circular, proof1, proof2
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event_name, start_date, end_date, 
            organizer, chief_guest, 
            psycopg2.Binary(circular_image), 
            psycopg2.Binary(proof1), 
            psycopg2.Binary(proof2)
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return f"Database error: {e}"

    return render_template("index.html")

@app.route("/events", methods=["GET"])
def get_events():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        events = cur.fetchall()
        
        # Prepare events data to return as JSON
        event_list = []
        for event in events:
            event_data = {
                "event_name": event[0],
                "start_date": event[1],
                "end_date": event[2],
                "organizer": event[3],
                "chief_guest": event[4],
                "circular": event[5].decode('utf-8'),  # Assuming the image is stored as base64 string
                "proof1": event[6].decode('utf-8'),
                "proof2": event[7].decode('utf-8')
            }
            event_list.append(event_data)
        
        cur.close()
        conn.close()
        return jsonify(event_list)

    except Exception as e:
        return f"Error fetching events: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)

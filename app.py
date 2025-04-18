from flask import Flask, request, render_template, jsonify
import os
import psycopg2
import base64

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    try:
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

        # Store into database
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (
                event_name, start_date, end_date, 
                organizer, chief_guest, 
                circular, proof1, proof2
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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

        return render_template("index.html")

    except Exception as e:
        return f"Database error: {e}", 500

@app.route("/events", methods=["GET"])
def get_events():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        rows = cur.fetchall()

        events = []
        for row in rows:
            events.append({
                "event_name": row[0],
                "start_date": row[1],
                "end_date": row[2],
                "organizer": row[3],
                "chief_guest": row[4],
                "circular": base64.b64encode(row[5]).decode("utf-8"),
                "proof1": base64.b64encode(row[6]).decode("utf-8"),
                "proof2": base64.b64encode(row[7]).decode("utf-8"),
            })

        cur.close()
        conn.close()
        return jsonify(events)

    except Exception as e:
        return f"Error fetching events: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, render_template, jsonify
import os
import psycopg2

app = Flask(__name__)

# Use DATABASE_URL from environment (Render provides this)
DATABASE_URL = os.environ.get("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/submit", methods=["POST"])
def api_submit():
    try:
        data = request.form
        files = request.files

        event_name = data.get("eve")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        organizer = data.get("organizer")
        chief_guest = data.get("chief_guest")

        circular_image = files["circular_image"].read()
        proof1 = files["proof1"].read()
        proof2 = files["proof2"].read()

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

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/events", methods=["GET"])
def api_get_events():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM events")
        events = cur.fetchall()

        event_list = []
        for event in events:
            event_data = {
                "event_name": event[0],
                "start_date": event[1],
                "end_date": event[2],
                "organizer": event[3],
                "chief_guest": event[4],
                "circular": event[5].decode('utf-8'),
                "proof1": event[6].decode('utf-8'),
                "proof2": event[7].decode('utf-8')
            }
            event_list.append(event_data)

        cur.close()
        conn.close()

        return jsonify(event_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

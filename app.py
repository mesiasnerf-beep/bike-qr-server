from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
def get_db():
    try:
        db = mysql.connector.connect(
            host="yamanote.proxy.rlwy.net",
            port=54195,
            user="root",
            password="lAimmTbnfyytLAqIHzfIfjAcxJelcNux",  # Your Railway MySQL password
            database="railway"
        )
        print("✅ Connected to MySQL")
        return db

    except Exception as e:
        print("❌ Database connection failed:")
        print(e)
        raise


# ---------- HOME ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "Bike QR Attendance API Running!"
    })


# ---------- GET ALL RIDERS ----------
@app.route("/riders", methods=["GET"])
def get_riders():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT * FROM riders")
        riders = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(riders)

    except Exception as e:
        import traceback

        print("========== SCAN ERROR ==========")
        traceback.print_exc()
        print("===============================")
        
        return jsonify({
            "error": str(e)
        }), 500


# ---------- DASHBOARD SUMMARY ----------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        # Today's date in Philippine time
        today = datetime.now(
            ZoneInfo("Asia/Manila")
        ).date()

        # Total Riders
        cursor.execute("""
            SELECT COUNT(*) AS totalRiders
            FROM riders
        """)
        total_riders = cursor.fetchone()["totalRiders"]

        # Today's Time In
        cursor.execute("""
            SELECT COUNT(*) AS totalTimeIn
            FROM attendance
            WHERE date = %s
            AND timeIn IS NOT NULL
            AND timeIn <> ''
        """, (today,))
        total_time_in = cursor.fetchone()["totalTimeIn"]

        # Today's Time Out
        cursor.execute("""
            SELECT COUNT(*) AS totalTimeOut
            FROM attendance
            WHERE date = %s
            AND timeOut IS NOT NULL
            AND timeOut <> ''
        """, (today,))
        total_time_out = cursor.fetchone()["totalTimeOut"]

        cursor.close()
        db.close()

        return jsonify({
            "totalRiders": total_riders,
            "totalTimeIn": total_time_in,
            "totalTimeOut": total_time_out
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500      

# ---------- REGISTER ----------
@app.route("/register", methods=["POST"])
def register():

    try:
        data = request.json

        db = get_db()
        cursor = db.cursor()

        sql = """
        INSERT INTO riders
        (
            fullName,
            gradeSection,
            lrn,
            address,
            bikeColor,
            bikeType,
            contactNumber,
            emergencyName,
            emergencyNumber,
            username,
            password
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
        """

        values = (
            data["fullName"],
            data["gradeSection"],
            data["lrn"],
            data["address"],
            data["bikeColor"],
            data["bikeType"],
            data["contactNumber"],
            data["emergencyName"],
            data["emergencyNumber"],
            data["username"],
            data["password"]
        )

        cursor.execute(sql, values)
        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            "message": "Rider Registered Successfully!"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():

    try:
        data = request.json

        username = data.get("username")
        password = data.get("password")

        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        sql = """
        SELECT
            id,
            fullName,
            gradeSection,
            lrn,
            address,
            bikeColor,
            bikeType,
            contactNumber,
            emergencyName,
            emergencyNumber,
            username
        FROM riders
        WHERE username=%s AND password=%s
        """

        cursor.execute(sql, (username, password))

        rider = cursor.fetchone()

        cursor.close()
        db.close()

        if rider:
            return jsonify(rider), 200

        return jsonify({
            "message": "Invalid username or password"
        }), 401

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# ---------- SCAN QR ----------
@app.route("/scan", methods=["POST"])
def scan_qr():

    try:
        data = request.json
        lrn = data.get("lrn")

        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        # Find rider
        cursor.execute(
            "SELECT * FROM riders WHERE lrn=%s",
            (lrn,)
        )

        rider = cursor.fetchone()

        if rider is None:
            cursor.close()
            db.close()

            return jsonify({
                "message": "Rider not found"
            }), 404

        # Today's date
        now = datetime.now(ZoneInfo("Asia/Manila"))

        today = now.date()

        current_time = now.strftime("%H:%M:%S")

        # Check today's attendance
        cursor.execute(
            """
            SELECT *
            FROM attendance
            WHERE lrn=%s
            AND date=%s
            """,
            (lrn, today)
        )

        attendance = cursor.fetchone()

        if attendance is None:

            cursor.execute(
                """
                INSERT INTO attendance
                (lrn, fullName, date, timeIn)
                VALUES (%s,%s,%s,%s)
                """,
                (
                    rider["lrn"],
                    rider["fullName"],
                    today,
                    current_time,
                ),
            )

            db.commit()

            action = "TIME IN"

        elif attendance["timeOut"] is None or attendance["timeOut"] == "":

            cursor.execute(
                """
                UPDATE attendance
                SET timeOut=%s
                WHERE id=%s
                """,
                (
                    current_time,
                    attendance["id"],
                ),
            )

            db.commit()

            action = "TIME OUT"

        else:

            action = "ALREADY COMPLETED"

        cursor.close()
        db.close()

        return jsonify({
            "action": action,
            "rider": {
                "fullName": rider["fullName"],
                "gradeSection": rider["gradeSection"],
                "lrn": rider["lrn"],
                "bikeType": rider["bikeType"]
            }
        })
    
    except Exception as e:
        import traceback

        traceback.print_exc()
        
        return jsonify({
            "error": str(e)
        }), 500


# ---------- GET ATTENDANCE ----------
@app.route("/attendance", methods=["GET"])
def get_attendance():

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        cursor.execute("""
            SELECT *
            FROM attendance
            ORDER BY id DESC
        """)

        attendance = cursor.fetchall()

        # Convert TIME fields to strings
        for row in attendance:
            if row["date"] is not None:
                row["date"] = row["date"].strftime("%Y-%m-%d")
                
            if row["timeIn"] is not None:
                row["timeIn"] = str(row["timeIn"])

            if row["timeOut"] is not None:
                row["timeOut"] = str(row["timeOut"])    

        cursor.close()
        db.close()

        return jsonify(attendance)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
def get_db():
    return mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=54195,
        user="root",
        password="lAimmTbnfyytLAqIHzfIfjAcxJelcNux",
        database="railway"
    )


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
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM riders")
        riders = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(riders)

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
        cursor = db.cursor(dictionary=True)

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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
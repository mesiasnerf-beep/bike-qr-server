from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Railway MySQL connection
db = mysql.connector.connect(
    host="yamanote.proxy.rlwy.net",
    port=54195,
    user="root",
    password="lAimmTbnfyytLAqIHzfIfjAcxJelcNux",
    database="railway"
)


@app.route("/")
def home():
    return "Bike QR Attendance API Running!"


# GET ALL RIDERS
@app.route("/riders", methods=["GET"])
def get_riders():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM riders")

    data = cursor.fetchall()

    cursor.close()

    return jsonify(data)


# REGISTER RIDER
@app.route("/register", methods=["POST"])
def register():

    data = request.json

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

    return jsonify({
        "message": "Rider Registered Successfully!"
    })


# RIDER LOGIN
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")
    password = data.get("password")

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
    WHERE username = %s AND password = %s
    """

    cursor.execute(sql, (username, password))

    rider = cursor.fetchone()

    cursor.close()

    if rider:
        return jsonify(rider), 200

    return jsonify({
        "message": "Invalid username or password"
    }), 401


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
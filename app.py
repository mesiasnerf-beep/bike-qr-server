from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="mysql.railway.internal",
    port=3306,
    user="root",
    password="lAimmTbnfyytLAqIHzfIfjAcxJelcNux",
    database="railway"
)

@app.route("/")
def home():
    return "Bike QR Attendance API Running!"

@app.route("/riders", methods=["GET"])
def get_riders():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM riders")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)


@app.route("/register", methods=["POST"])
def register():

    data = request.json

    cursor = db.cursor()

    sql = """
    INSERT INTO riders
    (fullName, gradeSection, lrn, address, bikeColor,
    bikeType, contactNumber, emergencyName,
    emergencyNumber, username, password)

    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)

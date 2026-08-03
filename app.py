import os
import platform
import subprocess
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure Database URL
# Uses Render PostgreSQL URL in production, or local SQLite database in development
db_url = os.environ.get("DATABASE_URL", "sqlite:///complaints.db")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace(
        "postgres://", "postgresql://", 1
    )  # Fix legacy URI scheme

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Define Database Model
class ComplaintModel(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    assigned_team = db.Column(db.String(30), default="Not Assigned")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "category": self.category,
            "description": self.description,
            "status": self.status,
            "team": self.assigned_team,
        }


# Initialize tables
with app.app_context():
    db.create_all()


# Helper function to validate phone (7-15 numeric digits)
def is_valid_phone(phone):
    return phone.isdigit() and (7 <= len(phone) <= 15)


# --- ROUTES ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if data.get("username") == "admin" and data.get("password") == "1234":
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/api/complaints", methods=["GET"])
def get_complaints():
    complaints = ComplaintModel.query.order_by(ComplaintModel.id.asc()).all()
    return jsonify([c.to_dict() for c in complaints])


@app.route("/api/complaints/<int:cid>", methods=["GET"])
def get_single_complaint(cid):
    complaint = ComplaintModel.query.get(cid)
    if complaint:
        return jsonify(complaint.to_dict())
    return jsonify({"error": "Not found"}), 404


@app.route("/api/complaints", methods=["POST"])
def create_complaint():
    data = request.json
    phone = data.get("phone", "")

    if not is_valid_phone(phone):
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid phone number! Must be 7-15 digits.",
                }
            ),
            400,
        )

    new_complaint = ComplaintModel(
        name=data["name"],
        phone=phone,
        category=data["category"],
        description=data["description"],
        status="Pending",
        assigned_team="Not Assigned",
    )

    db.session.add(new_complaint)
    db.session.commit()

    return jsonify({"status": "success", "id": new_complaint.id}), 201


@app.route("/api/complaints/<int:cid>", methods=["PUT"])
def update_complaint(cid):
    complaint = ComplaintModel.query.get(cid)
    if not complaint:
        return jsonify({"status": "error", "message": "Not found"}), 404

    data = request.json
    if "status" in data and data["status"]:
        complaint.status = data["status"]
    if "team" in data and data["team"]:
        complaint.assigned_team = data["team"]

    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/api/complaints/<int:cid>", methods=["DELETE"])
def delete_complaint_route(cid):
    complaint = ComplaintModel.query.get(cid)
    if not complaint:
        return jsonify({"status": "error", "message": "Not found"}), 404

    db.session.delete(complaint)
    db.session.commit()
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
import os
import platform
import subprocess
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 1. SECURITY & CONFIGURATION
# ---------------------------------------------------------------------------

# Helper function to generate a rate limit key based on IP + Username
def get_login_rate_limit_key():
    # Grabs the username submitted in JSON or Form data, fallback to 'anonymous'
    data = request.get_json(silent=True) or request.form
    username = data.get('username', 'anonymous')
    
    # Combines client IP + attempted username (e.g. "192.168.1.1:admin")
    return f"{get_remote_address()}:{username}"

# Fetch secret key and admin credentials from environment variables (with local fallbacks)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')       # Default local username: admin
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1234')        # Default local password: 1234

# Session Cookie Security Settings
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents client-side JS from stealing session cookies
app.config['SESSION_COOKIE_SECURE'] = True    # Enforces HTTPS-only cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Helps mitigate CSRF attacks

# Setup Rate Limiter to prevent brute-force attacks
# Setup Rate Limiter (No default global limits, only specific routes will be limited)
limiter = Limiter(
    get_remote_address,
    app=app
)

# ---------------------------------------------------------------------------
# 2. DATABASE CONFIGURATION (PostgreSQL / SQLite)
# ---------------------------------------------------------------------------
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

# Initialize database tables
with app.app_context():
    db.create_all()

# Helper function to validate phone (7-15 numeric digits)
def is_valid_phone(phone):
    return phone.isdigit() and (7 <= len(phone) <= 15)


# ---------------------------------------------------------------------------
# 3. PAGE ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

# Rate limit: Max 5 attempts per minute to prevent brute-forcing admin page
# UPDATED: Now uses the custom key_func
@limiter.limit("5 per minute", key_func=get_login_rate_limit_key)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_page():
    return render_template("admin.html")


# ---------------------------------------------------------------------------
# 4. API ROUTES
# ---------------------------------------------------------------------------

# UPDATED: Now uses the custom key_func to protect API login endpoint
@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute", key_func=get_login_rate_limit_key)  
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    
    # Check credentials against environment variables (ADMIN_USERNAME & ADMIN_PASSWORD)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
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
    data = request.json or {}
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

    data = request.json or {}
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
import os
from flask import Flask, jsonify, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ---------------------------------------------------------------------------
# 1. PATH & FLASK INITIALIZATION (Vercel-Safe Absolute Paths)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# ---------------------------------------------------------------------------
# 2. SECURITY & CONFIGURATION
# ---------------------------------------------------------------------------

def get_login_rate_limit_key():
    data = request.get_json(silent=True) or request.form
    username = data.get('username', 'anonymous')
    return f"{get_remote_address()}:{username}"

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1234')

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

limiter = Limiter(
    get_remote_address,
    app=app
)

# ---------------------------------------------------------------------------
# 3. DATABASE CONFIGURATION (Neon PostgreSQL / Local SQLite)
# ---------------------------------------------------------------------------
default_sqlite_path = f"sqlite:///{os.path.join(BASE_DIR, 'complaints.db')}"
db_url = os.environ.get("DATABASE_URL", default_sqlite_path)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Auto-append sslmode=require for Neon PostgreSQL remote connections
if db_url.startswith("postgresql://") and "sslmode=" not in db_url:
    delimiter = "&" if "?" in db_url else "?"
    db_url = f"{db_url}{delimiter}sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.instance_path = os.path.join(BASE_DIR, "instance")

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
# 4. PAGE ROUTES
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@limiter.limit("5 per minute", key_func=get_login_rate_limit_key)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_page():
    return render_template("admin.html")


# ---------------------------------------------------------------------------
# 5. API ROUTES
# ---------------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute", key_func=get_login_rate_limit_key)  
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    
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
    app.run(host="0.0.0.0", debug=True, port=5000)
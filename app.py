from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from werkzeug.security import generate_password_hash, check_password_hash
from lead_scoring import calculate_lead_score

app = Flask(__name__)

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///leads.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT CONFIG
app.config["JWT_SECRET_KEY"] = "super-secret-real-estate-key"

# INIT EXTENSIONS
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ======================
# MODELS
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

    leads = db.relationship("Lead", backref="agent", lazy=True)


class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    intent = db.Column(db.String(20))
    budget = db.Column(db.Integer)
    timeline = db.Column(db.String(50))
    score = db.Column(db.Integer)
    priority = db.Column(db.String(20))

    status = db.Column(db.String(50), default="New")
    source = db.Column(db.String(50))
    assigned_agent = db.Column(db.String(100))
    notes = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


with app.app_context():
    db.create_all()

# ======================
# ROUTES
# ======================

@app.route("/")
def home():
    return {"message": "Real Estate Lead Automation API Running"}


# REGISTER USER
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = generate_password_hash(data["password"])

    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# LOGIN USER (JWT TOKEN)
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token
    })


# CREATE LEAD (USER AUTHENTICATED)
@app.route("/leads", methods=["POST"])
@jwt_required()
def create_lead():

    data = request.json

    user_id = get_jwt_identity()

    score, priority = calculate_lead_score(data)

    new_lead = Lead(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        intent=data["intent"],
        budget=data.get("budget"),
        timeline=data.get("timeline"),
        score=score,
        priority=priority,
        source=data.get("source"),
        assigned_agent=data.get("assigned_agent"),
        notes=data.get("notes"),
        user_id=user_id
    )

    db.session.add(new_lead)
    db.session.commit()

    return jsonify({
        "message": "Lead created successfully",
        "score": score,
        "priority": priority
    }), 201


# GET LEADS FOR LOGGED USER
@app.route("/leads", methods=["GET"])
@jwt_required()
def get_user_leads():

    user_id = get_jwt_identity()

    leads = Lead.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": lead.id,
            "name": lead.name,
            "priority": lead.priority,
            "status": lead.status
        }
        for lead in leads
    ])


# UPDATE LEAD
@app.route("/leads/update/<int:id>", methods=["PATCH"])
@jwt_required()
def update_lead(id):

    lead = Lead.query.get_or_404(id)
    data = request.get_json()

    lead.status = data.get("status", lead.status)
    lead.assigned_agent = data.get("assigned_agent", lead.assigned_agent)
    lead.source = data.get("source", lead.source)
    lead.notes = data.get("notes", lead.notes)

    db.session.commit()

    return jsonify({"message": "Lead updated successfully"})


if __name__ == "__main__":
    app.run(debug=True)
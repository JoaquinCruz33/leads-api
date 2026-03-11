from flask import Flask, request, jsonify, send_file 
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)


from werkzeug.security import generate_password_hash, check_password_hash
from lead_scoring import calculate_lead_score
from automation import handle_hot_lead
from whatsapp import send_whatsapp

app = Flask(__name__)

# ACTIVAR CORS
CORS(app)

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

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    intent = db.Column(db.String(50))
    budget = db.Column(db.Integer)
    timeline = db.Column(db.String(50))

    score = db.Column(db.Integer)
    priority = db.Column(db.String(20))
    status = db.Column(db.String(50), default="New")


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

    data = request.get_json()

    budget = int(data["budget"]) if data.get("budget") else 0
    data["budget"] = budget

    score, priority = calculate_lead_score(data)

    current_user = get_jwt_identity()
    
    user_id = get_jwt_identity()

    new_lead = Lead(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        intent=data["intent"],
        budget=budget,
        timeline=data["timeline"],
        score=score,
        priority=priority,
        status="New",
        user_id=current_user
    )

    db.session.add(new_lead)
    db.session.commit()

    if priority == "Hot":
        handle_hot_lead(new_lead)

    return jsonify({
        "message": "Lead created successfully",
        "priority": priority
    }), 201


# GET LEADS FOR LOGGED USER
@app.route("/leads", methods=["GET"])
@jwt_required()
def get_leads():

    user_id = get_jwt_identity()

    leads = Lead.query.filter_by(user_id=user_id).all()

    result = []

    for lead in leads:
        result.append({
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "intent": lead.intent,
            "budget": lead.budget,
            "timeline": lead.timeline,
            "score": lead.score,
            "priority": lead.priority,
            "status": lead.status
        })

    return jsonify(result)

@app.route("/export")
@jwt_required()
def export_leads():

    user_id = get_jwt_identity()

    leads = Lead.query.filter_by(user_id=user_id).all()

    data = []

    for lead in leads:
        data.append({
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "intent": lead.intent,
            "budget": lead.budget,
            "priority": lead.priority,
            "status": lead.status
        })

    df = pd.DataFrame(data)

    file = "leads.xlsx"
    df.to_excel(file, index=False)

    return send_file(file, as_attachment=True)

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
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import joblib

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = "budgetbee_secret_key"  # change to something secure
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budgetbee.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Database Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --- Load ML Model (dummy/real pipeline) ---
try:
    pipeline = joblib.load("budgetbee_pipeline.joblib")
except:
    # Fallback dummy model if not found
    class DummyModel:
        def predict(self, X):
            return ["Misc" for _ in X]
    pipeline = DummyModel()

# --- Routes ---

@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists! Try another.", "danger")
            return redirect(url_for("register"))

        # Save new user
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user"] = user.username
            flash("Welcome back, " + user.username + "!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    desc = request.form["description"]
    amt = request.form["amount"]
    category = pipeline.predict([desc])[0]
    return render_template(
        "result.html",
        description=desc,
        amount=amt,
        category=category,
        user=session["user"]
    )

# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if not exist
    app.run(debug=True)


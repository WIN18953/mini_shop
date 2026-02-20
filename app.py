from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Product, Cart
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ========================
# HOME
# ========================
@app.route("/")
def home():
    return render_template("home.html")
# ========================
# PRODUCTS
# ========================
@app.route("/products")
def products():
    all_products = Product.query.all()
    return render_template("products.html", products=all_products)


# ========================
# REGISTER
# ========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        # สร้าง user ใหม่
        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ========================
# LOGIN (ชั่วคราวก่อน)
# ========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

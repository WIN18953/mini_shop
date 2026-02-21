from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Product, Cart
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "mysecretkey"
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
# ADMIN - ADD PRODUCT
# ========================
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        image = request.form.get("image")

        # กัน error ถ้าฟอร์มส่งไม่ครบ
        if not name or not price or not description:
            return "Please fill all required fields"

        new_product = Product(
            name=name,
            price=float(price),
            description=description,
            image=image
        )

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for("products"))

    return render_template("admin.html")


# ========================
# REGISTER
# ========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

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
# LOGIN
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


# ========================
# LOGOUT
# ========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    # ถ้ายังไม่มี cart ใน session ให้สร้างใหม่
    if "cart" not in session:
        session["cart"] = []

    # เพิ่ม product_id ลงไป
    session["cart"].append(product_id)

    # บอก Flask ว่ามีการแก้ไข session
    session.modified = True

    # กลับไปหน้าตะกร้า
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    if "cart" in session:
        for product_id in session["cart"]:
            product = Product.query.get(product_id)

            if product:
                cart_items.append(product)
                total += product.price

    return render_template("cart.html", items=cart_items, total=total)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

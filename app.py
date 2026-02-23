from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Product, Order
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecretkey"
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
# ADMIN
# ========================
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():

    if not current_user.is_admin:
        return "Unauthorized", 403

    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        description = request.form.get("description")
        image = request.form.get("image")

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


# ========================
# PRODUCT DETAIL
# ========================
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)


# ========================
# ADD TO CART (มือโปร)
# ========================
@app.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]

    for item in cart:
        if item["id"] == product_id:
            item["quantity"] += 1
            session.modified = True
            return redirect(url_for("cart"))

    cart.append({
        "id": product_id,
        "quantity": 1
    })

    session.modified = True
    return redirect(url_for("cart"))


# ========================
# CART
# ========================
@app.route("/cart")
@login_required
def cart():

    cart_items = []
    total = 0

    for item in session.get("cart", []):
        product = Product.query.get(item["id"])

        if product:
            subtotal = product.price * item["quantity"]
            total += subtotal

            cart_items.append({
                "product": product,
                "quantity": item["quantity"],
                "subtotal": subtotal
            })

    return render_template("cart.html", items=cart_items, total=total)


# ========================
# REMOVE FROM CART
# ========================
@app.route("/remove_from_cart/<int:product_id>")
@login_required
def remove_from_cart(product_id):

    cart = session.get("cart", [])

    for item in cart:
        if item["id"] == product_id:
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                cart.remove(item)
            break

    session.modified = True
    return redirect(url_for("cart"))


# ========================
# CHECKOUT
# ========================
@app.route("/checkout", methods=["POST"])
@login_required
def checkout():

    cart = session.get("cart", [])

    if not cart:
        return redirect(url_for("cart"))

    total = 0

    for item in cart:
        product = Product.query.get(item["id"])
        if product:
            total += product.price * item["quantity"]

    new_order = Order(
        user_id=current_user.id,
        total_price=total
    )

    db.session.add(new_order)
    db.session.commit()

    session["cart"] = []

    return redirect(url_for("order_history"))


# ========================
# ORDER HISTORY
# ========================
@app.route("/orders")
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("orders.html", orders=orders)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
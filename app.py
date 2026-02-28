from flask import session
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask import Flask, render_template
from models import db
from flask_login import LoginManager
from models import db, User
from models import db, User, Product
from models import db, User, Product, Cart, Order, OrderItem

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        # ✅ เช็คว่ามี email ซ้ำไหม
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("อีเมลนี้ถูกใช้แล้ว ❌")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("สมัครสมาชิกสำเร็จ 🎉")
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("เข้าสู่ระบบสำเร็จ 🎉")
            return redirect(url_for("home"))
        else:
            flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง ❌")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ออกจากระบบแล้ว 👋")
    return redirect(url_for("home"))

@app.route("/products")
def products():
    all_products = Product.query.all()
    return render_template("products.html", products=all_products)

from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']

        new_product = Product(
            name=name,
            price=price,
            description=description,
            image=image
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!")
        return redirect(url_for('products'))

    return render_template('add_product.html')

@app.route('/delete_product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully 🗑")
    return redirect(url_for('products'))

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):

    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}

    cart = session['cart']
    id = str(id)

    if id in cart:
        cart[id] += 1
    else:
        cart[id] = 1

    session['cart'] = cart
    session.modified = True

    return redirect('/products')

@app.route('/cart')
def cart():

    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}

    cart = session.get('cart', {})

    products = []
    total = 0

    for id, quantity in cart.items():
        product = Product.query.get(int(id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

    return render_template('cart.html', products=products, total=total)

@app.route('/clear')
def clear():
    session.clear()
    return "Session cleared!"

@app.route('/increase/<int:id>')
def increase(id):

    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}

    cart = session['cart']
    id = str(id)

    if id in cart:
        cart[id] += 1

    session['cart'] = cart
    session.modified = True

    return redirect('/cart')

@app.route('/decrease/<int:id>')
def decrease(id):

    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}

    cart = session['cart']
    id = str(id)

    if id in cart:
        cart[id] -= 1
        if cart[id] <= 0:
            del cart[id]

    session['cart'] = cart
    session.modified = True

    return redirect('/cart')

@app.route('/remove/<int:id>')
def remove(id):

    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}

    cart = session['cart']
    id = str(id)

    if id in cart:
        del cart[id]

    session['cart'] = cart
    session.modified = True

    return redirect('/cart')

from flask_login import login_required, current_user

@app.route('/checkout')
@login_required
def checkout():

    # ดึง cart ของ user ปัจจุบัน
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        return redirect('/cart')

    total = 0

    # สร้าง Order ใหม่
    new_order = Order(user_id=current_user.id, total_price=0)
    db.session.add(new_order)
    db.session.commit()   # commit ก่อนเพื่อให้ได้ order.id

    # วนสร้าง OrderItem
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            subtotal = product.price * item.quantity
            total += subtotal

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )
            db.session.add(order_item)

    # อัปเดต total_price
    new_order.total_price = total

    # ลบ cart ของ user
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    return render_template('success.html', total=total)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
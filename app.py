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
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(id)
    session.modified = True

    flash("Added to cart!")
    return redirect('/')

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    return render_template('cart.html', cart=cart)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
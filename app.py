from flask import Flask, render_template
from models import db, User, Product, Cart
from flask_login import LoginManager

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


@app.route("/")
def home():
    return "<h1>Mini Shop is Running 🚀</h1>"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

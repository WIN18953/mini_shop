from flask import Flask
from models import db
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/")
def home():
    return "Mini Shop is Running 🚀"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
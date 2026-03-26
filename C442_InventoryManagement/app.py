from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from model import InventoryModel

app = Flask(__name__)
app.secret_key = "change-this-to-a-real-secret-key"
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):

    model = InventoryModel()
    row = model.get_user_by_id(user_id)
    user = model.build_user_object(row)
    model.close()
    return user


# Import blueprints after app/login setup
from auth import auth_bp
from inventory import inventory_bp

app.register_blueprint(auth_bp)
app.register_blueprint(inventory_bp)

if __name__ == "__main__":
    app.run(debug=True)
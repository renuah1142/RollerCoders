from flask import Flask
from flask_jwt_extended import JWTManager
from App.database import db, init_db
from App.models.user import User  # Import the User model
from App.controllers.ingredient import ingredient_ctrl
from App.views.recipe import recipe_views
from App.views.ingredient import ingredient_views  

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('config.Config')

    init_db(app)  # Initialize the database
    
    jwt = JWTManager(app)
    
    @jwt.user_lookup_loader 
    def user_lookup_callback(jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    app.register_blueprint(ingredient_ctrl)
    app.register_blueprint(recipe_views)
    app.register_blueprint(ingredient_views)

    return app
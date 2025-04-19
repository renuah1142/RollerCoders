import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from App.views.auth import auth_views
from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import (
    create_user, 
    get_all_users_json, 
    get_all_users, 
    initialize
)

# Create and configure app
app = create_app()
migrate = get_migrate(app)

# Setup JWT and CORS
jwt = JWTManager(app)
CORS(app)

# Register Blueprints


'''
Database Init Command
'''
@app.cli.command("init", help="Initialize the database")
def init():
    """Initialize the database and add default data."""
    db.drop_all()
    db.create_all()
    print("Database initialized.")
    
    # Add default user `bob` with password `bobpass`
    create_user("bob", "bobpass")
    print("Default user 'bob' created with password 'bobpass'.")

'''
User Commands
'''
user_cli = AppGroup('user', help='User object commands') 

@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli)

'''
Test Commands
'''
test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))

@test.command("ingredient", help="Run Ingredient tests")
@click.argument("type", default="all")
def ingredient_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "IngredientUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "IngredientIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "Ingredient"]))

app.cli.add_command(test)

if __name__ == "__main__":
    app.run()


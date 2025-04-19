# App/views/ingredient_views.py
import os, json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from App.database import db
from App.models.ingredient import Ingredient

ingredient_views = Blueprint('ingredient_views', __name__, template_folder='../templates')

# load local JSON if you still want it:
JSON_PATH = os.path.join(os.path.dirname(__file__), 'ingredient_list.json')
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    LOCAL_INGREDIENTS = json.load(f).get('meals', [])

def get_user_ingredients(user_id):
    return Ingredient.query.filter_by(user_id=user_id).all()

def add_ingredient_to_user(user_id, ingredient_id, name, quantity):
    item = Ingredient.query.filter_by(user_id=user_id, ingredient_id=ingredient_id).first()
    if item:
        item.quantity += quantity
    else:
        item = Ingredient(user_id=user_id,
                          ingredient_id=ingredient_id,
                          name=name,
                          quantity=quantity)
        db.session.add(item)
    db.session.commit()

def remove_ingredient_from_user(user_id, ingredient_id):
    item = Ingredient.query.filter_by(user_id=user_id, ingredient_id=ingredient_id).first()
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True

@ingredient_views.route('/dashboard', methods=['GET','POST'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    # use local JSON instead of API:
    all_ingredients = LOCAL_INGREDIENTS

    if request.method == 'POST':
        q = request.form.get('query','').strip().lower()
        search_results = [ing for ing in all_ingredients if q in ing['strIngredient'].lower()]
        search_error = (len(search_results) == 0)
    else:
        search_results = all_ingredients
        search_error = False

    user_items = get_user_ingredients(user_id)
    user_ids = {ui.ingredient_id for ui in user_items}

    return render_template('dashboard.html',
        search_results=search_results,
        user_ingredients=user_items,
        user_ingredient_ids=user_ids,
        search_error=search_error,
        username=current_user.username
    )

@ingredient_views.route('/ingredients/add', methods=['POST'])
@jwt_required()
def add_ingredient_view():
    user_id = get_jwt_identity()
    ing_id  = request.form['ingredient_id']
    name    = request.form['name']
    qty     = int(request.form.get('quantity',1))
    add_ingredient_to_user(user_id, ing_id, name, qty)
    flash('Ingredient added.')
    return redirect(url_for('ingredient_views.dashboard'))

@ingredient_views.route('/ingredients/remove', methods=['POST'])
@jwt_required()
def remove_ingredient_view():
    user_id = get_jwt_identity()
    ing_id  = request.form['ingredient_id']
    removed = remove_ingredient_from_user(user_id, ing_id)
    flash('Removed.' if removed else 'Not found.')
    return redirect(url_for('ingredient_views.dashboard'))

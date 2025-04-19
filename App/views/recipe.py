# App/views/recipe.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.models.saved_recipe import SavedRecipe
from App.database import db
import requests

recipe_views = Blueprint('recipe_views', __name__)

@recipe_views.route('/recipes/search', methods=['GET'])
@jwt_required()
def search_recipes():
    q = request.args.get('q','')
    try:
        res = requests.get(
            'https://www.themealdb.com/api/json/v1/1/search.php',
            params={'s': q},
            timeout=5
        )
        res.raise_for_status()
        meals = res.json().get('meals') or []
        return jsonify(meals), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@recipe_views.route('/recipes/saved', methods=['POST'])
@jwt_required()
def save_recipe():
    data = request.get_json() or {}
    user_id = get_jwt_identity()
    try:
        sr = SavedRecipe(
            user_id=user_id,
            recipe_id=data['idMeal'],
            title=data['strMeal'],
            missing_ingredients=data.get('missing', [])
        )
        db.session.add(sr)
        db.session.commit()
        return jsonify(sr.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@recipe_views.route('/recipes/saved', methods=['GET'])
@jwt_required()
def list_saved():
    user_id = get_jwt_identity()
    recs = SavedRecipe.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in recs]), 200

@recipe_views.route('/recipes/saved/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_saved(id):
    user_id = get_jwt_identity()
    r = SavedRecipe.query.get_or_404(id)
    if r.user_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    try:
        db.session.delete(r)
        db.session.commit()
        return jsonify({}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

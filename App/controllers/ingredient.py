# App/controllers/ingredient.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db
from App.models.ingredient import Ingredient

ingredient_ctrl = Blueprint('ingredient_ctrl', __name__)

@ingredient_ctrl.route('/ingredients', methods=['POST'])
@jwt_required()
def create_ingredient():
    data = request.get_json() or {}
    user_id = get_jwt_identity()
    try:
        ing = Ingredient(
            user_id=user_id,
            ingredient_id=data['ingredient_id'],
            name=data['name'],
            quantity=int(data.get('quantity', 1))
        )
        db.session.add(ing)
        db.session.commit()
        return jsonify(ing.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@ingredient_ctrl.route('/ingredients', methods=['GET'])
@jwt_required()
def list_ingredients():
    user_id = get_jwt_identity()
    items = Ingredient.query.filter_by(user_id=user_id).all()
    return jsonify([i.to_dict() for i in items]), 200

@ingredient_ctrl.route('/ingredients/<int:id>', methods=['PUT'])
@jwt_required()
def update_ingredient(id):
    data = request.get_json() or {}
    user_id = get_jwt_identity()
    ing = Ingredient.query.get_or_404(id)
    if ing.user_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    try:
        ing.quantity = int(data.get('quantity', ing.quantity))
        db.session.commit()
        return jsonify(ing.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@ingredient_ctrl.route('/ingredients/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_ingredient(id):
    user_id = get_jwt_identity()
    ing = Ingredient.query.get_or_404(id)
    if ing.user_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    try:
        db.session.delete(ing)
        db.session.commit()
        return jsonify({}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

from App.database import db

class SavedRecipe(db.Model):
    __tablename__ = 'saved_recipes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    missing_ingredients = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'title': self.title,
            'missing_ingredients': self.missing_ingredients
        }
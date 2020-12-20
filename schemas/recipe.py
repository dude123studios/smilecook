from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema
from flask import url_for



def validate_num_of_servings(n):
    if n < 1:
        raise ValidationError('Number of servings must be greater than 0')
    elif n > 50:
        raise ValidationError('Number of servings must be less than 50')


class RecipeSchema(Schema):
    class Meta():
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=40)])
    description = fields.String(validate=[validate.Length(max=100)])
    directions = fields.String(validate=[validate.Length(max=500)])
    is_public = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, only=['id', 'username'])
    num_of_servings = fields.Integer(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    cover_image = fields.Method(serialize='dump_cover_image_url')
    ingredients = fields.String(validate=[validate.Length(max=100)])

    def dump_cover_image_url(self, recipe):
        if recipe.cover_image:
            return url_for('static', filename='images/cover_images/{}'.format(recipe.cover_image), _external=True)
        return url_for('static', filename='images/assets/default-recipe.jpg', _external=True)

    @validates('cook_time')
    def validate_cook_time(self, value):
        if value < 1:
            raise ValidationError('Cook time must be greater than 0')
        if value > 300:
            raise ValidationError('This is going to take FOREVER')


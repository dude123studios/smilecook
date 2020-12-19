from flask import request
from flask_restful import Resource
from http import HTTPStatus
from schemas.recipe import RecipeSchema
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from utils import save_image
from extensions import image_set
import os
from schemas.pagination import RecipePaginationSchema
from webargs import fields
from webargs.flaskparser import use_kwargs
recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_cover_schema = RecipeSchema(only=('cover_image',))
recipe_pagination_schema = RecipePaginationSchema()

class RecipeListResource(Resource):

    @use_kwargs({'page':fields.Int(missing=1), 'per_page':fields.Int(missing=20)})
    def get(self,page, per_page):
        paginated_recipes = Recipe.get_all_published(page, per_page)
        return recipe_pagination_schema.dump(paginated_recipes).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        data = request.get_json()
        current_user = get_jwt_identity()
        data, errors = recipe_schema.load(data=request.get_json())
        if errors:
            return {'message': 'Validation errors', 'errors': errors}
        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()

        return recipe_schema.dump(recipe).data, HTTPStatus.CREATED


class RecipeCoverUploadResource(Resource):
    @jwt_required
    def put(self, recipe_id):
        file = request.files.get('cover_image')
        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not supported'}, HTTPStatus.BAD_REQUEST
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        if recipe.user_id != get_jwt_identity():
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if recipe.cover_image:
            cover_image_path = image_set.path(recipe.cover_image, folder='cover_images')
            if os.path.exists(cover_image_path):
                os.remove(cover_image_path)
        filename = save_image(file, 'cover_images')
        recipe.cover_image = filename
        recipe.save()
        return recipe_cover_schema.dump(recipe).data, HTTPStatus.OK


class RecipeResource(Resource):

    @jwt_optional
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.is_public is False and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def patch(self, recipe_id):
        json_data = request.get_json()

        data, errors = recipe_schema.load(data=json_data, partial=('name',))
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions
        recipe.save()

        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def put(self, recipe_id):
        data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        data, errors = recipe_schema.load(data=data)
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST
        recipe.name = data.get('name')
        recipe.description = data.get('description')
        recipe.num_of_servings = data.get('num_of_servings')
        recipe.cook_time = data.get('cook_time')
        recipe.directions = data.get('directions')
        recipe.save()
        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.delete()
        return {}, HTTPStatus.NO_CONTENT


class RecipePublicResource(Resource):

    @jwt_required
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        if get_jwt_identity() != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.is_public = True
        recipe.save()
        return

    @jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'recipe not found'}, HTTPStatus.NOT_FOUND
        if get_jwt_identity() != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.is_public = False
        recipe.save()
        return {}, HTTPStatus.NO_CONTENT

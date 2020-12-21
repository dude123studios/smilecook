from flask import Flask, request
from flask_restful import Api
from flask_migrate import Migrate
from flask_uploads import configure_uploads, patch_request_class
import os

from extensions import db, jwt, image_set, cache, limiter
from resources.token import TokenResource, RefreshResource, RevokeResource, blacklist
from resources.user import (UserListResource, MeResource, UserResource, UserRecipeListResource, UserActivateResource,
                            UserAvatarUploadResource)
from resources.recipe import RecipeListResource, RecipeResource, RecipePublicResource, RecipeCoverUploadResource

def create_app():

    env = os.environ.get('ENV','Development')
    if env == 'Production':
        config_str = 'config.ProductionConfig'
    elif env == 'Staging':
        config_str = 'config.StagingConfig'
    else:
        config_str = 'config.DevelopmentConfig'
    app = Flask(__name__)
    app.config.from_object(config_str)

    register_extensions(app)
    register_resources(app)
    return app
def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    configure_uploads(app, image_set)
    patch_request_class(app, 4*1024*1024)
    cache.init_app(app)
    limiter.init_app(app)
    @limiter.request_filter
    def ip_whitelist():
        return request.remote_addr == '127.0.0.1'
    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in blacklist
def register_resources(app):
    api = Api(app)

    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')

    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserListResource, '/users')
    api.add_resource(MeResource, '/me')

    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(RecipePublicResource, '/recipes/<int:recipe_id>/publish')
    api.add_resource(RecipeCoverUploadResource, '/recipes/<int:recipe_id>/cover')

if __name__ == '__main__':
    app = create_app()
    app.run()
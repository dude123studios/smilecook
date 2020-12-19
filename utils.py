from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import uuid
from flask_uploads import extension
from extensions import image_set
from PIL import Image
import os

def hash_password(password):
    return pbkdf2_sha256.hash(password)

def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

def generate_token(email, salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt=salt)

def save_image(image, folder):
    filename = '{}.{}'.format(uuid.uuid4(), extension(image.filename))
    image_set.save(image, folder=folder, name=filename)
    filename = compress_image(filename=filename, folder=folder)
    return filename

def verify_token(token, max_age=(30*60), salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    try:
        email = serializer.loads(token, max_age=max_age, salt=salt)
    except:
        return False
    return email
def compress_image(filename, folder):
    filepath = image_set.path(filename=filename, folder=folder)
    image = Image.open(filepath)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    if max(image.width, image.height) > 1600:
        maxsize = (1600, 1600)
        image.thumbnail(maxsize, Image.ANTIALIAS)
    compressed_filename = '{}.jpg'.format(uuid.uuid4())
    compressed_filepath = image_set.path(compressed_filename, folder=folder)
    image.save(compressed_filepath, optimizer=True, quality=50)
    os.remove(filepath)
    return compressed_filename
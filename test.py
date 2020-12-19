from app import create_app
from models.user import User
from models.recipe import Recipe
app = create_app()


user = User(username='jackthegod85',email='jackthegodyeah@gmail.com',password='ahQa')
user.save()
pizza = Recipe(name='Tomato', description='de', num_of_servings=2,cook_time=30,directions='This is how you make it', user_id=user.id)
pizza.save()

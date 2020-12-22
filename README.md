# smilecook
project for learning api development

This is a project I am creating in order to learn api development based on a book, "Python API Development Fundamentals" by *_PACKT_*

It is an API allowing for users to share recipes. They can search for recipes to find ones which they like, JWT tokens are used as authentication,
data is all stored in *_POSTGRESQL_* data bases, image compression is taken place, and data goes through serialization and deserialization using Marshmallow.
Finally, cool usefull features such as pagination, and auto emailing are added, and the entire api is built on top a front end server. 

I am using a *_Heroku_* cloud service to host this api. The code here does not include the changes made for the server to run. For example, it doesnt have the Procfile, or main.py, both of which initialize the server and initialize the database. This is because that would be far too case specific.

If you would like to test my api, the endpoints are listed at the end of app.py, and they are all linked to http://smilecook-was-taken.herokuapp.com/{api route}

The next step in the procces of networking is to build a frontend. This could be in the form of a messaging system GUI. The next thing I may work on is a python front end app for this project, since the service of Heroku lasts forever. 

Thank for reading 

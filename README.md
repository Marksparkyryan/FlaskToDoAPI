# FlaskToDoAPI

FlaskToDo is a demonstration of Flask's API framework (flask_restful) in the form of a to-do list. A pre-built Angualar frontend was provided and the objective was to build a 
backend with endpoints that handled each unique request. Additionally, all endpoints were protected by the requirement of a signed web token.


<br/>

# installation

1. cd into your directory of projects (or wherever you prefer to keep your clones)
2. git clone ```https://github.com/Marksparkyryan/FlaskToDoAPI.git``` to clone the app
3. ```virtualenv .venv``` to create your virtual environment
4. ```source .venv/bin/activate``` to activate the virtual environment
5. ```pip install -r FlaskToDoAPI/requirements.txt``` to install app requirements
6. ```python app.py``` to serve the site to your local host (in DEBUG mode)
7. visit ```http://127.0.0.1:8000/``` to see the list! 

Note: If testing, config.TESTING should be True to prevent testing on main database 

<br/>

# usage

By default, DEBUG mode is set to True in config.py. This is good for testing but not good for deployment. If deploying, make sure
DEBUG is set to False.

If in DEBUG, use the following user to log in:

email: sparky@email.com
password: password


<br/>


# credits

Treehouse Techdegree Project 10

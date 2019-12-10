import json

from flask import Flask, g, render_template, flash, redirect, url_for, session

import auth
import config
import forms
import models

from resources.todos import todos_api


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.register_blueprint(todos_api, url_prefix='/api/v1')


@app.route('/', methods=["GET"])
def my_todos():
    """Route for handling GET requests

    Returns:
        200 response -- template response of index.html
    """
    return render_template('index.html')


@app.route('/login', methods=("GET", "POST"))
def login():
    """Route for handling the logging in of user

    Returns:
        redirect response -- if successfull log in (attaches generated
        token to session)
    """
    form = forms.LoginForm()
    if form.validate_on_submit():
        if not auth.verify_password(form.email.data, form.password.data):
            flash(message='Username and password are invalid.')
        else:
            token = g.user.generate_auth_token()
            session['token'] = token.decode('ascii')
            flash(
                message=f"You've been logged in with token {session['token']}")
            return redirect(url_for('my_todos'))
    return render_template('login.html', form=form)


if __name__ == '__main__':
    models.initialize()
    if config.DEBUG and not config.TESTING:
        try:
            models.User.create_user(
                username='sparky',
                email='sparky@email.com',
                password='password'
            )
        except Exception:
            pass
        try:
            with open('mock/todos.json') as mocktodos:
                json_reader = json.load(mocktodos)
                for todo in json_reader:
                    models.ToDo.create(
                        created_by=1,
                        **todo
                    )
        except models.IntegrityError:
            pass

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)

import json

from flask import Flask, g, jsonify, render_template, flash, redirect, url_for, make_response, session

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
    return render_template('index.html')


@app.route('/login', methods=("GET", "POST"))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        if not auth.verify_password(form.email.data, form.password.data):
            print("not logged in")
            pass
        else:
            token = g.user.generate_auth_token()
            session['token'] = token.decode('ascii') 
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
            print("Mock user already exists")
        try:
            with open('mock/todos.json') as mocktodos:
                json_reader = json.load(mocktodos)
                for todo in json_reader:
                    models.ToDo.create(
                        created_by=1,
                        **todo
                    )
        except Exception:
            print("Mock todos already exist")

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
    
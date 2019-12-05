import json

from flask import Flask, g, jsonify, render_template, flash, redirect, url_for, make_response

import auth
import config
import forms
import models

from resources.todos import todos_api


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.register_blueprint(todos_api, url_prefix='/api/v1')


@app.route('/')
# @auth.auth.login_required
def my_todos():
    return render_template('index.html')


@app.route('/login', methods=("GET", "POST"))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            auth.verify_password(form.email.data, form.password.data)
        except models.User.DoesNotExist:
            flash("Your email or password does not match!", "error")
        else:
            response = make_response()
            token = g.user.generate_auth_token()
            response.headers['Authorization'] = "Token " + token.decode('ascii')
            return response
    return render_template('login.html', form=form)


if __name__ == '__main__':
    models.initialize()
    if config.DEBUG:
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
    
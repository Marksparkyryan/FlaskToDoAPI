from flask_wtf import FlaskForm as Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ]
    )
    password = StringField(
        "Password",
        validators=[
            DataRequired(),
        ]
    )
    
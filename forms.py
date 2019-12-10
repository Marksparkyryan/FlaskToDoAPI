from flask_wtf import FlaskForm as Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    """Form for handling the logging in of user.
    
    Arguments:
        Form {class} -- Accepts user email and password from the
        submitted form data
    """
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
    
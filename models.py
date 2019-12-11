from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *

import config

DATABASE = SqliteDatabase('todos.sqlite')
HASHER = PasswordHasher()


class User(Model):
    """Model describing the user

    Attributes:
        username {string} -- user's username
        email {string} -- user's email
        password {string} -- user's password

    Methods:
        create_user -- class method handling the creation of a new user
        set_password -- handles the hashing of user's password
        verify_password -- checks password against hash
        generate_auth_token -- creates timed web token and returns as
        json
        verify_auth_token -- checks for valid token and returns user

    Returns:
        User instance -- instance of user
    """
    username = CharField(max_length=12, unique=True)
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        """Method that should be used to create a new user. This checks
        for existing emails and usernames prior to registering the user.

        Arguments:
            username {string} -- max length of 12
            email {string} -- user's email address
            password {string} -- user's password no character
            limitiations

        Raises:
            Exception: if user already exists (username and/or email)

        Returns:
            User instance -- if user is succussfully created
        """
        email = email.lower()
        try:
            cls.select().where(
                (cls.email == email) | (cls.username**username)
            ).get()
        except cls.DoesNotExist:
            user = cls(username=username, email=email)
            user.password = user.set_password(password)
            user.save()
            return user
        else:
            raise Exception("User with that email or username already exists")

    @staticmethod
    def set_password(password):
        """Handles the hashing of the user's submitted password. 

        Arguments:
            password {string} -- user's password

        Returns:
            string -- a hashed version of password
        """
        return HASHER.hash(password)

    def verify_password(self, password):
        """Handles verifying submitted user passwords.

        Arguments:
            password {string} -- user's password

        Returns:
            True -- if password matches database hash
            False -- if password does not match database hash
        """
        try:
            return HASHER.verify(self.password, password)
        except:
            return False

    def generate_auth_token(self, expires=6000):
        """Handles the creation of a cryptographically signed and timed
        web token.

        Keyword Arguments:
            expires {int} -- expiry of token in seconds (default: {6000})

        Returns:
            string -- a cryptographically signed and timed web token
            holding the user's id
        """
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """Handles verifying the submitted web token. Returns user if
        the token is valid, None if not valid.

        Arguments:
            token {string} -- cryptographically signed and timed
        web token

        Returns:
            User instance -- if valid token, user instance that is
            stored in the token
            None -- if token was not valid or expired
        """
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(User.id == data['id'])
            return user


class ToDo(Model):
    """Model describing each item on the todo list.

    Arguments:
        Model {class} --  Base model from Peewee

    Attributes:
        name {string} -- displayed value on the list, max length 256
        completed {boolean} -- completion status of item
        edited {boolean} -- True if the item data has been changed
        created_by {int} -- id of the User instance
    """
    name = CharField(max_length=256, unique=True)
    completed = BooleanField(default=False, null=True)
    edited = BooleanField(default=False, null=True)
    created_by = ForeignKeyField(User, related_name='todo_set')

    class Meta:
        database = DATABASE


def initialize():
    """Builds the database with User and ToDo tables
    """
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([User, ToDo], safe=True)
    DATABASE.close()

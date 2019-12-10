import datetime
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
        instance -- instance of user
    """
    username = CharField(max_length=12, unique=True)
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE
    
    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:
            cls.select().where(
                (cls.email==email)|(cls.username**username)
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
        return HASHER.hash(password)
    
    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    def generate_auth_token(self, expires=6000):
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})
    
    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(User.id==data['id'])
            return user


class ToDo(Model):
    """Schema describing an item in the todo list
    """
    name = CharField(max_length=256, unique=True)
    completed = BooleanField(default=False)
    edited = BooleanField(default=False)
    created_by = ForeignKeyField(User, related_name='todo_set')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([User, ToDo], safe=True)
    DATABASE.close()

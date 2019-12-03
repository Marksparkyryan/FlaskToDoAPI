import datetime

from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *

import config

DATABASE = SqliteDatabase('todos.sqlite')
HASHER = 

class User(Model):
    """Schema describing a user instance
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


class Todo(Model):
    """Schema describing a todo instance.
    """
    title = CharField(max_length=256, unique=True)
    completed = BooleanField(default=False)
    created_by = ForeignKeyField(User, related_name='todo_set')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect(reuse_if_open=True)
    DATABASE.create_tables([Todo], safe=True)
    DATABASE.close()

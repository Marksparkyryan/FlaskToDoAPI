from flask import g, session

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

import models

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')
auth = MultiAuth(token_auth, basic_auth)


@basic_auth.verify_password
def verify_password(email, password):
    try:
        user = models.User.get(
            (models.User.email==email)
        )
        if not user.verify_password(password):
            return False
    except models.User.DoesNotExist:
        return False
    else:
        # print("using basic auth", email, password)
        g.user = user
        return True


@token_auth.verify_token
def verify_token(token):
    if not token:
        try:
            token = session['token']
        except:
            pass
    user = models.User.verify_auth_token(token)
    if user is not None:
        print("Using token auth", token)
        g.user = user
        return True
    return False
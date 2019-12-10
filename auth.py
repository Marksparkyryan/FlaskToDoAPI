from flask import g, session

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

import models

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')
auth = MultiAuth(token_auth, basic_auth)


@basic_auth.verify_password
def verify_password(email, password):
    """Verifies submitted password and returns True and sets global user
    to that user. If not verified, returns False.

    Arguments:
        email {string} -- user email
        password {string} -- user password

    Returns:
        True -- if user was verified
        False -- if user was not verified or does not exist
    """
    try:
        user = models.User.get(
            (models.User.email==email)
        )
        if not user.verify_password(password):
            return False
    except models.User.DoesNotExist:
        return False
    else:
        g.user = user
        return True


@token_auth.verify_token
def verify_token(token):
    """Verifies token supplied in request. If token is valid, return
    True and set global user to requesting user. If token is not valid,
    returns False.

    Arguments:
        token {string} -- cryptographic token in string format

    Returns:
        True -- and sets global user to requesting user
        False -- if token is not valid or expired
    """
    if not token:
        try:
            token = session['token']
        except:
            pass
    user = models.User.verify_auth_token(token)
    if user is not None:
        g.user = user
        return True
    return False

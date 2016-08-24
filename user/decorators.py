from functools import wraps
from flask import session, request, redirect, url_for, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id') is None:
            return redirect(url_for('user_app.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin') is False:
            if session.get('id') is None:
                return redirect(url_for('user_app.login', next=request.url))
            else:
                abort(403)
        return f(*args, **kwargs)
    return decorated_function

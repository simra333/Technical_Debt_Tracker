from functools import wraps
from flask import session, redirect, url_for, jsonify

def ui_login_required(f):
    @wraps(f)
    def decorated_functions(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_functions

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function
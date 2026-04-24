from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(plain_password: str) -> str:
    if not plain_password or not isinstance(plain_password, str):
        raise ValueError("Password must be a non-empty string.")
    return generate_password_hash(plain_password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    if not plain_password or not password_hash:
        return False 
    return check_password_hash(password_hash, plain_password)
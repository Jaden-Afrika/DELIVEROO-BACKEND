from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.user import User


def create_user(full_name: str, email: str, password: str, role="user") -> User:
    user = User(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email: str, password: str):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

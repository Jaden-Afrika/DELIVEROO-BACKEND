from app.models.user import User
from app.models.enums import UserRole


def create_user(full_name: str, email: str, password: str, role="user") -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        role=role if role in (UserRole.user.value, UserRole.admin.value) else UserRole.user.value,
    )
    return user


def authenticate_user(email: str, password: str):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if user.check_password(password):
        return user
    return None

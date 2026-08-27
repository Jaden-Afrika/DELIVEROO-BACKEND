from datetime import datetime, timezone
from app.utils import utcnow

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from app.models.enums import UserRole


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.password_hash = user.password
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("role", UserRole.user.value)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.admin.value)
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[(r.value, r.name) for r in UserRole],
        default=UserRole.user.value,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=utcnow)
    updated_at = models.DateTimeField(
        default=utcnow,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        app_label = "app"
        db_table = "users"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name or self.email

    def __str__(self):
        return self.email

    def to_dict(self):
        created = self.created_at.astimezone(timezone.utc) if self.created_at else None
        return {
            "id": self.id,
            "name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": created.isoformat() if created else None,
        }

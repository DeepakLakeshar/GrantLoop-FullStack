import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Required because USERNAME_FIELD = 'email' alone doesn't change
    AbstractUser's default manager — without this, create_user() still
    expects username as its first positional argument."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", extra_fields.get("role", "donor"))
        extra_fields.setdefault("full_name", extra_fields.get("full_name", ""))
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("full_name", extra_fields.get("full_name", "Admin"))
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    ADR-003: custom User via AbstractUser, no Profile table. Role lives
    directly on this model so every permission check is a single field
    access, never a join.

    Login identifier is email, not Django's default username — the
    frontend's LoginPayload sends {email, password}. The inherited
    `username` field still exists (AbstractUser requires it) but is
    auto-populated from email in save() and never shown to the user;
    `full_name` is the real display name, serialized to the frontend's
    User.username field (see UserPublicSerializer) since that's the
    display-name slot the frontend contract already expects.
    """

    ROLE_CHOICES = [
        ("donor", "Donor"),
        ("ngo", "NGO"),
        ("institution", "Institution"),
        ("execution_partner", "Execution partner"),
        ("admin", "Admin"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        indexes = [models.Index(fields=["role"])]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.full_name} ({self.role})"

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Manager for User model where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    # Remove the inherited username field entirely
    username = None

    # Email is the sole identifier for authentication
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        help_text="Mobile number for OTP and booking alerts",
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Required for concession eligibility",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        help_text="Application-level role: admin or user",
    )

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["phone_number"], name="idx_user_phone"),
            models.Index(fields=["email"], name="idx_user_email"),
        ]
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.role})"

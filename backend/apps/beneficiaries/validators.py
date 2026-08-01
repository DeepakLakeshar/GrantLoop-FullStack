import re
from datetime import date
from django.core.exceptions import ValidationError


def validate_phone_number(value: str):
    """
    Validates that a phone number matches international formats (+123456789).
    """
    if not re.match(r'^\+?1?\d{9,15}$', value):
        raise ValidationError("Enter a valid phone number.")


def validate_date_of_birth(value: date):
    """
    Validates that the date of birth is not in the future.
    """
    if value and value > date.today():
        raise ValidationError("Date of birth cannot be in the future.")


def validate_government_id(value: str):
    """
    Placeholder/hook to perform government ID format validations if needed.
    """
    if not value or len(value.strip()) < 3:
        raise ValidationError("Government ID must be at least 3 characters long.")


def validate_profile_image(file):
    """
    Validates uploaded profile image specifications (size, content type, extension).
    """
    MAX_SIZE = 5 * 1024 * 1024
    if file.size > MAX_SIZE:
        raise ValidationError("Profile photo size must be less than 5MB.")

    VALID_MIMES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if hasattr(file, "content_type") and file.content_type not in VALID_MIMES:
        raise ValidationError("Profile photo must be a valid image (JPEG, PNG, GIF, WEBP).")

    ext = file.name.split('.')[-1].lower()
    VALID_EXTS = ["jpg", "jpeg", "png", "gif", "webp"]
    if ext not in VALID_EXTS:
        raise ValidationError("Profile photo file extension must be jpg, jpeg, png, gif, or webp.")

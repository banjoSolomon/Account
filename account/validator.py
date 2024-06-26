from django.core.exceptions import ValidationError


def validate_pin(pin):
    if len(pin) < 4:
        raise ValidationError("Pin must be four digits ")

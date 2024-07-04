from django.core.exceptions import ValidationError


def validate_pin(pin):
    if len(pin) < 4:
        raise ValidationError("Pin must be four digits ")


def validate_withdraw(withdraw):
    if withdraw < 1:
        raise ValidationError("Withdrawal amount cannot be negative")

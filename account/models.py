from django.db import models
from django.conf import settings
from .utility import generate_account_number
from .validator import validate_pin
from user.models import User


# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=10, default=generate_account_number, unique=True, primary_key=True)
    pin = models.CharField(max_length=4, validators=[validate_pin])
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    Account_TYPE = [
        ('S', 'SAVING'),
        ('C', 'CURRENT'),
        ('D', 'DOOM'),
    ]

    def __str__(self):
        return f" {self.balance} {self.account_type} {self.account_number}"

    account_type = models.CharField(max_length=1, choices=Account_TYPE, default='S')


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('DEB', 'DEBIT'),
        ('CRE', 'CREDIT'),
        ('TRA', 'TRANSFER'),
    ]
    TRANSACTION_STATUS = [
        ('S', 'SUCCESSFUL'),
        ('F', 'FAIL'),
        ('P', 'PENDING'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')

    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPE, default='CRE')

    transaction_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)

    transaction_status = models.CharField(max_length=1, choices=TRANSACTION_STATUS, default='S')

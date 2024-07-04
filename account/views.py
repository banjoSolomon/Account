from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


import account
from .validator import validate_withdraw
from rest_framework.permissions import IsAuthenticated
from .models import Account, Transaction
from .serializers import AccountSerializer, AccountCreateSerializer, DepositWithdrawSerializer, WithdrawSerializer, \
    TransferSerializer


# Create your views here.


# class CreateAccount(CreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer
#
#
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountCreateSerializer


# class ListAccount(ListCreateAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer

# def get_queryset(self):
#     return Account.objects.all()
#
# def get_serializer_class(self):
#     return AccountCreateSerializer


# @api_view(['GET', 'POST'])
# def list_account(request):
#     if request.method == 'GET':
#         accounts = Account.objects.all()
#         serializer.py = AccountSerializer(accounts, many=True)
#         return Response(serializer.py.data, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         serializer.py = AccountCreateSerializer(data=request.data)
#         if serializer.py.is_valid(raise_exception=True):
#             serializer.py.save()
#             return Response(serializer.py.data, status=status.HTTP_201_CREATED)


# class AccountDetails(RetrieveUpdateDestroyAPIView):
#     queryset = Account.objects.all()
#     serializer_class = AccountCreateSerializer
# def get(self, request):
#     accounts = Account.objects.all()
#     serializer.py = AccountSerializer(accounts, many=True)
#     return Response(serializer.py.data, status=status.HTTP_200_OK)
#
# def post(self, request):
#     serializer.py = AccountCreateSerializer(data=request.data)
#     if serializer.py.is_valid(raise_exception=True):
#         serializer.py.save()
#         return Response(serializer.py.data, status=status.HTTP_201_CREATED)

# def get(self, request, pk):
#     account = get_object_or_404(Account, pk=pk)
#     serializer.py = AccountCreateSerializer(account, many=True)
#     return Response(serializer.py.data, status=status.HTTP_200_OK)
#
# def put(self, request, pk):
#     account = get_object_or_404(Account, pk=pk)
#     serializer.py = AccountCreateSerializer(account, data=request.data)
#     if serializer.py.is_valid(raise_exception=True):
#         serializer.py.save()
#         return Response(serializer.py.data, status=status.HTTP_200_OK)
#
# def delete(self, request, pk):
#     account = get_object_or_404(Account, pk=pk)
#     account.delete()
#     return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(["GET", "PUT", "PATCH", "DELETE"])
# def account_detail(request, pk):
#     account = get_object_or_404(Account, pk=pk)
#     if request.method == "GET":
#         serializer.py = AccountSerializer(account)
#         return Response(serializer.py.data, status=status.HTTP_200_OK)
#     elif request.method == "PUT":
#         serializer.py = AccountSerializer(account, data=request.data)
#         if serializer.py.is_valid(raise_exception=True):
#             serializer.py.save()
#             return Response(serializer.py.data, status=status.HTTP_200_OK)
#     elif request.method == "DELETE":
#         account.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(["POST"])
# def deposit(request):
#     account_number = request.data['account_number']
#     amount = Decimal(request.data['amount'])
#     account = get_object_or_404(Account, pk=account_number)
#     account.balance += amount
#     account.save()
#     Transaction.objects.create(
#         account=account,
#         amount=amount,
#     )
#     return Response({"message": "Transaction successful"}, status=status.HTTP_200_OK)


class Deposit(APIView):
    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = serializer.data['account_number']
        amount = Decimal(serializer.data['amount'])

        transaction_details = {}
        account = get_object_or_404(Account, pk=account_number)
        balance = account.balance
        balance += amount
        Account.objects.filter(account_number=account_number).update(balance=balance)
        Transaction.objects.create(
            account=account,
            amount=amount,

        )
        transaction_details['account_number'] = account_number
        transaction_details['amount'] = amount
        transaction_details['transaction_type'] = 'CREDIT'
        return Response(data=transaction_details, status=status.HTTP_200_OK)


class Withdraw(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_number = request.data['account_number']
        amount = request.data['amount']
        if validate_withdraw(amount):
            return Response(data={"message": "Invalid withdrawal amount"}, status=status.HTTP_400_BAD_REQUEST)
        pin = request.data["pin"]
        account = get_object_or_404(Account, pk=account_number)
        if account.pin == pin:
            if account.balance > amount:
                account.balance -= Decimal(amount)
                account.save()
                Transaction.objects.create(
                    account=account,
                    amount=amount,
                    transaction_type='DEB'
                )
            else:
                return Response(data={"message": "Insufficient"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(data={"message": "Invalid pin"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "Withdraw successful"}, status=status.HTTP_200_OK)


class TransferViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender_account_from = serializer.data['sender_account']
        receiver_account = serializer.data['receiver_account']
        amount = Decimal(serializer.data['amount'])
        transaction_details = {}
        sender_account_from = get_object_or_404(Account, pk=sender_account_from)
        receiver_account_to = get_object_or_404(Account, pk=receiver_account)
        balance = sender_account_from.balance
        transaction_details = {}
        if balance > amount:
            balance -= amount
            Account.objects.filter(pk=sender_account_from).update(balance=balance)
        else:
            return Response({"message": "Insufficient Funds"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            transferred_balances = receiver_account_to.balance + amount
            Account.objects.filter(pk=receiver_account).update(balance=transferred_balances)
        except Account.DoesNotExist:
            return Response({"message": "Transaction failed"}, status=status.HTTP_400_BAD_REQUEST)
        Transaction.objects.create(
            account=sender_account_from,
            amount=amount,
            transaction_type='TRANSFER',
        )
        transaction_details['receiver account'] = receiver_account
        transaction_details['amount'] = amount
        transaction_details['transaction type'] = 'TRANSFER'
        return Response(data=transaction_details, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response(data="Method not supported", status=status.HTTP_405_METHOD_NOT_ALLOWED)

# auth/jwt/create
class CheckBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        account = get_object_or_404(Account, user=user.id)
        balance_details = {'account number': account.account_number, 'balance': account.balance}
        message = f'''
        your new balance is
        {account.balance}
        thank you for banking with jaguda'''
        send_mail(subject="JAGUDA BANK", message= message,
                  from_email=['adewunmi@gmail.com'],
                  recipient_list=[f'{user.email}'])
        return Response(data=balance_details, status=status.HTTP_200_OK)

    # receiver_account_to = get_object_or_404(Account, pk=request.data)
    # balance = sender_account_from.balance
    # transaction_details
    # amount = request.data['amount']
    # if account.balance > amount:
    #     account.balance -= Decimal(amount)
    #     receiver_account_to.balance += Decimal(amount)
    #     account.save()
    #     receiver_account_to.save()
    #     Transaction.objects.create(
    #         account=account,
    #         amount=amount,
    #         transaction_type='DEB',
    #     )
    #     Transaction.objects.create(
    #         account=receiver_account_to,
    #         amount=amount,
    #         transaction_type='CREDIT',
    #     )

# @api_view(["POST"])
# def withdraw(request):
#     account_number = request.data['account_number']
#     amount = request.data['amount']
#     pin = request.data['pin']
#     account = get_object_or_404(Account, pk=account_number)
#     if account.pin == pin:
#         if account.balance > amount:
#             account.balance -= Decimal(amount)
#             account.save()
#             Transaction.objects.create(
#                 account=account,
#                 amount=amount,
#                 transaction_type='DEB',
#             )
#         else:
#             return Response({"message": "Insufficient Funds"}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(data={"message": "Invalid PIN"}, status=status.HTTP_400_BAD_REQUEST)
#
#     return Response({"message": "Transaction successful"}, status=status.HTTP_200_OK)

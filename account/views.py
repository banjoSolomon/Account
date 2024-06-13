from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Account
from .serializers import AccountSerializer


# Create your views here.
@api_view()
def list_account(request):
    accounts = Account.objects.all()
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view()
def account_detail(request, pk):
    account = Account.objects.get(pk=pk)
    serializer = AccountSerializer(account)
    return Response(serializer.data, status=status.HTTP_200_OK)

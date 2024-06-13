from django.shortcuts import render, HttpResponse


# Create your views here.
# localHost:800/demo/hello

def say_hello(request):
    return HttpResponse("Hello, welcome to django")


def welcome(request):
    return render(request, 'index.html')


from django.shortcuts import render
from django.http import HttpResponse

def view_test(request):
    print("thing")
    return HttpResponse("test")
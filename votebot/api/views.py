from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from api.models import *

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.serializers import *

def verify_secret(secret):
    host_match = Host.objects.filter(secret=secret)
    if len(host_match) == 1:
        return host_match[0]
    superuser_match = Superuser.objects.filter(secret=secret)
    if len(superuser_match) == 1:
        return superuser_match[0]
    return None

@api_view(['POST'])
def view_auth_superuser(request):
    if "username" in request.data and "password" in request.data:
        match = Superuser.objects.filter(username__iexact=request.data["username"], password=request.data["password"])
        if len(match) == 1:
            return JsonResponse({"status": "SUCCESS_SUPERUSER_AUTHENTICATED", "superuser": match[0].export(include_secret=True)})
        return JsonResponse({"status": "ERROR_INVALID_SUPERUSER_AUTH", "message": "Invalid superuser username or password"}, status="401")
    return JsonResponse({"status": "ERROR_BAD_SUPERUSER_LOGIN_REQUEST", "message": "Request must include username and password fields"}, status="400")

@api_view(['POST'])
def view_auth_host(request):
    if "username" in request.data and "password" in request.data:
        match = Host.objects.filter(username__iexact=request.data["username"], password=request.data["password"])
        if len(match) == 1:
            return JsonResponse({"status": "SUCCESS_HOST_AUTHENTICATED", "host": match[0].export(include_secret=True)})
        return JsonResponse({"status": "ERROR_INVALID_HOST_AUTH", "message": "Invalid host username or password"}, status="401")
    return JsonResponse({"status": "ERROR_BAD_HOST_LOGIN_REQUEST", "message": "Request must include username and password fields"}, status="400")
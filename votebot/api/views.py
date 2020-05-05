from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings

from api.models import *
from api import responses

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import random

from api.serializers import *

def generate_secret(length=64):
    possible_chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    secret = ""
    for i in range(length):
        secret += possible_chars[random.randrange(0, len(possible_chars))]
    return secret

def resp(status, data, status_code="200"):
    data["status"] = status
    return JsonResponse(data, status=status_code)

def authenticate(request, allowed, host_usernames=[]):
    if not "secret" in request.GET:
        return responses.ERROR_MISSING_SECRET
    user = verify_secret(request.GET["secret"])
    if user == None:
        return responses.ERROR_INVALID_AUTH
    if type(user) == Host:
        if user.username not in host_usernames:
            return responses.ERROR_NOT_AUTHORIZED
    else:
        if type(user) not in allowed and user != "ROOT":
            return responses.ERROR_NOT_AUTHORIZED
    return True

def verify_secret(secret):
    if secret == settings.ROOT_SECRET:
        return "ROOT"
    host_match = Host.objects.filter(secret=secret)
    if host_match:
        return host_match[0]
    superuser_match = Superuser.objects.filter(secret=secret)
    if superuser_match:
        return superuser_match[0]
    return None

@api_view(['POST'])
def view_auth_superuser(request):
    if "username" in request.data and "password" in request.data:
        match = Superuser.objects.filter(username=request.data["username"], password=request.data["password"])
        if match:
            return resp("SUCCESS_SUPERUSER_AUTHENTICATED", {"superuser": match[0].export(include_secret=True)})
        return responses.ERROR_INVALID_SUPERUSER_AUTH
    return responses.ERROR_BAD_SUPERUSER_LOGIN_REQUEST

@api_view(['POST'])
def view_auth_host(request):
    if "username" in request.data and "password" in request.data:
        match = Host.objects.filter(username=request.data["username"], password=request.data["password"])
        if match:
            return resp("SUCCESS_HOST_AUTHENTICATED", {"host": match[0].export(include_secret=True)})
        return responses.ERROR_INVALID_HOST_AUTH
    return responses.ERROR_BAD_HOST_LOGIN_REQUEST

@api_view(['GET', 'POST'])
def view_superusers(request):
    auth = authenticate(request, [Superuser])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_SUPERUSERS_GET", {"superusers": [su.export() for su in Superuser.objects.all()]})
        elif request.method == "POST":
            ser = SuperuserPOSTSerializer(data=request.data)
            if ser.is_valid():
                new = ser.save()
                new.secret = generate_secret()
                new.save()
                return resp("SUCCESS_SUPERUSER_POST", {"superuser": new.export(include_secret=True)})
            return responses.ERROR_BAD_POST_DATA(ser.errors)
    else:
        return auth

@api_view(['GET', 'PUT', 'DELETE'])
def view_superusers_id(request, id):
    auth = authenticate(request, [Superuser])
    if auth == True:
        match = Superuser.objects.filter(username=id)
        if not match:
            return responses.ERROR_RESOURCE_NOT_FOUND
        if request.method == "GET":
            return resp("SUCCESS_SUPERUSER_GET", {"superuser": match[0].export()})
        elif request.method == "PUT":
            ser = SuperuserPUTSerializer(match[0], data=request.data)
            if ser.is_valid():
                obj = ser.save()
                return resp("SUCCESS_SUPERUSER_PUT", {"superuser": obj.export()})
            return responses.ERROR_BAD_PUT_DATA(ser.errors)
        elif request.method == "DELETE":
            match[0].delete()
            return resp("SUCCESS_SUPERUSER_DELETE", {})
    else:
        return auth

@api_view(['GET', 'POST'])
def view_hosts(request):
    auth = authenticate(request, [Superuser])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_HOSTS_GET", {"hosts": [host.export() for host in Host.objects.all()]})
        elif request.method == "POST":
            print(request.data)
            ser = HostPOSTSerializer(data=request.data)
            server_port = request.data["server_port"]
            try:
                x = int(server_port)
            except:
                return responses.ERROR_BAD_POST_DATA({"server_port": ["port must be an integer"]})
            if ser.is_valid():
                new = ser.save()
                new.secret = generate_secret()
                new.save()
                return resp("SUCCESS_HOST_POST", {"host": new.export(include_secret=True)})
            return responses.ERROR_BAD_POST_DATA(ser.errors)
    else:
        return auth

@api_view(['GET', 'PUT', 'DELETE'])
def view_hosts_id(request, id):
    auth = authenticate(request, [Superuser], [id])
    if auth == True:
        match = Host.objects.filter(username=id)
        if not match:
            return responses.ERROR_RESOURCE_NOT_FOUND
        if request.method == "GET":
            return resp("SUCCESS_HOST_GET", {"host": match[0].export()})
        elif request.method == "PUT":
            ser = HostPUTSerializer(match[0], data=request.data)
            if ser.is_valid():
                obj = ser.save()
                return resp("SUCCESS_HOST_PUT", {"host": obj.export()})
            return responses.ERROR_BAD_PUT_DATA(ser.errors)
        elif request.method == "DELETE":
            match[0].delete()
            return resp("SUCCESS_HOST_DELETE", {})
    else:
        return auth
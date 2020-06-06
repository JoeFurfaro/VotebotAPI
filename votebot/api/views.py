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
import uuid
import pathlib
import shutil
import configparser
import subprocess
import os

from api.serializers import *

server_processes = {}

def process_is_running(pid):
    global server_processes
    if pid not in server_processes:
        return False
    process = server_processes[pid]
    if process.poll() is None:
        return True
    return False

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
            ser = HostPOSTSerializer(data=request.data)
            server_port = request.data["server_port"]
            try:
                server_port = str(int(server_port))
            except:
                return responses.ERROR_BAD_POST_DATA({"server_port": ["port must be an integer"]})
            if ser.is_valid():
                new = ser.save()
                new.secret = generate_secret()
                new.save()
                root_path = str(pathlib.Path().absolute())
                server_path = root_path + "/servers/" + new.username
                shutil.copytree(root_path + "/server_template", server_path)
                new_server = Server.objects.create(id=str(uuid.uuid4()), path=server_path, owner=new, port=server_port)
                new.voting_server = new_server
                new.save()
                server_config = configparser.ConfigParser()
                server_config.read(server_path + "/server.ini")
                server_config["GENERAL"]["server_port"] = server_port
                with open(server_path + "/server.ini", "w") as config_file:
                    server_config.write(config_file)
                plugin_config = configparser.ConfigParser()
                plugin_config.read(server_path + "/plugins/votebot/votebot.ini")
                plugin_config["GENERAL"]["api_auth_key"] = settings.ROOT_SECRET
                with open(server_path + "/plugins/votebot/votebot.ini", "w") as config_file:
                    plugin_config.write(config_file)
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
            if match[0].voting_server:
                shutil.rmtree(match[0].voting_server.path)
            match[0].delete()
            return resp("SUCCESS_HOST_DELETE", {})
    else:
        return auth

@api_view(['GET', 'POST'])
def view_host_sessions(request, id):
    auth = authenticate(request, [Superuser], [id])
    if auth == True:
        match = Host.objects.filter(username=id)
        if not match:
            return responses.ERROR_RESOURCE_NOT_FOUND
        if request.method == "GET":
            return resp("SUCCESS_SESSIONS_GET", {"sessions": match[0].export_session_details()})
        elif request.method == "POST":
            ser = SessionSerializer(data=request.data)
            if ser.is_valid():
                obj = ser.save()
                obj.host = match[0]
                obj.observer_key = generate_secret(length=32)
                obj.save()
                return resp("SUCCESS_SESSION_POST", {"session": obj.export()})
            return responses.ERROR_BAD_POST_DATA(ser.errors)
    else:
        return auth

@api_view(['GET', 'PUT', 'DELETE'])
def view_sessions_id(request, id):
    match = Session.objects.filter(id=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].host.username])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_SESSION_GET", {"session": match[0].export()})
        elif request.method == "PUT":
            ser = SessionSerializer(match[0], data=request.data)
            if ser.is_valid():
                obj = ser.save()
                return resp("SUCCESS_SESSION_PUT", {"session": obj.export()})
            return responses.ERROR_BAD_PUT_DATA(ser.errors)
        elif request.method == "DELETE":
            match[0].delete()
            return resp("SUCCESS_SESSION_DELETE", {})
    else:
        return auth

@api_view(['GET', 'POST'])
def view_session_topics(request, id):
    match = Session.objects.filter(id=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].host.username])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_TOPICS_GET", {"topics": [topic.export() for topic in match[0].topics.all()]})
        elif request.method == "POST":
            ser = TopicSerializer(data=request.data)
            if ser.is_valid():
                obj = ser.save()
                match[0].topics.add(obj)
                match[0].save()
                return resp("SUCCESS_TOPIC_POST", {"topic": obj.export()})
            return responses.ERROR_BAD_PUT_DATA(ser.errors)
    else:
        return auth
        
@api_view(['GET', 'DELETE', 'POST'])
def view_session_voters(request, id):
    match = Session.objects.filter(id=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].host.username])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_SESSION_VOTERS_GET", {"voters": [voter.export() for voter in match[0].voters.all()]})
        elif request.method == "POST":
            if "voter_id" in request.data:
                voter_match = Voter.objects.filter(id=request.data["voter_id"])
                if voter_match:
                    voter = voter_match[0]
                    if voter not in match[0].voters.all():
                        match[0].voters.add(voter)
                    return resp("SUCCESS_SESSION_VOTERS_POST", {"voter": voter.export()})
                return responses.ERROR_RESOURCE_NOT_FOUND
            return responses.ERROR_BAD_POST_DATA()
        elif request.method == "DELETE":
            if "voter_id" in request.data:
                voter_match = Voter.objects.filter(id=request.data["voter_id"])
                if voter_match:
                    voter = voter_match[0]
                    if voter in match[0].voters.all():
                        match[0].voters.remove(voter)
                    return resp("SUCCESS_SESSION_VOTERS_DELETE", {"voter": voter.export()})
                return responses.ERROR_RESOURCE_NOT_FOUND
            return responses.ERROR_BAD_DELETE_DATA()
    else:
        return auth

@api_view(['GET', 'DELETE'])
def view_session_topics_id(request, id, tid):
    match = Session.objects.filter(id=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    topic_match = Topic.objects.filter(id=tid)
    if not topic_match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].host.username])
    if auth == True:
        if request.method == "DELETE":
            topic_match[0].delete()
            return resp("SUCCESS_TOPIC_DELETE", {})
        elif request.method == "GET":
            return resp("SUCCESS_TOPIC_GET", {"topic": topic_match[0].export()})
    else:
        return auth

@api_view(['GET', 'POST'])
def view_host_voters(request, id):
    match = Host.objects.filter(username=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].username])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_VOTERS_GET", {"voters": [voter.export() for voter in match[0].voters.all()]})
        elif request.method == "POST":
            ser = VoterSerializer(data=request.data)
            if ser.is_valid():
                obj = ser.save()
                obj.parent_host = match[0]
                obj.secret = generate_secret(length=64)
                match[0].voters.add(obj)
                match[0].save()
                obj.save()
                return resp("SUCCESS_VOTERS_POST", {"voter": obj.export()})
            return responses.ERROR_BAD_PUT_DATA(ser.errors)
    else:
        return auth

@api_view(['GET', 'PUT', 'DELETE'])
def view_voters_id(request, id):
    match = Voter.objects.filter(id=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].parent_host.username])
    if auth == True:
        if request.method == "GET":
            return resp("SUCCESS_VOTER_GET", {"voter": match[0].export()})
        elif request.method == "PUT":
            ser = VoterSerializer(match[0], data=request.data)
            if ser.is_valid():
                obj = ser.save()
                return resp("SUCCESS_VOTER_PUT", {"voter": obj.export()})
            return responses.ERROR_BAD_PUT_DATA(ser.errors)
        elif request.method == "DELETE":
            match[0].delete()
            return resp("SUCCESS_VOTER_DELETE", {})
    else:
        return auth

@api_view(['POST'])
def view_launch(request, id):
    global server_processes
    match = Session.objects.filter(id=id)
    if not match:
        return responses.ERROR_RESOURCE_NOT_FOUND
    auth = authenticate(request, [Superuser], [match[0].host.username])
    if auth == True:
        host = match[0].host
        server = host.voting_server
        if server.process_id == "" or not process_is_running(server.process_id):
            server.reset()
            plugin_config = configparser.ConfigParser()
            plugin_config.read(server.path + "/plugins/votebot/votebot.ini")
            plugin_config["GENERAL"]["voting_session_id"] = match[0].id
            with open(server.path + "/plugins/votebot/votebot.ini", "w") as config_file:
                plugin_config.write(config_file)
            process = subprocess.Popen([settings.PYTHON_PATH, server.path + "/manage.py", "runserver"])
            server_processes[str(process.pid)] = process
            print("Starting voting server on port " + str(server.port))
            server.process_id = str(process.pid)
            server.session = match[0]
            server.save()
            return resp("SUCCESS_STARTING_SERVER", {}, status_code=200)
        return resp("ERROR_SERVER_BUSY", {"message": "Your server is already in use!"}, status_code="503")
    else:
        return auth

@api_view(['GET'])
def view_servers(request):
    global server_processes
    auth = authenticate(request, [Superuser], [])
    if auth == True:
        online_servers = []
        servers = Server.objects.exclude(session=None)
        for server in servers:
            if server.process_id != "":
                if process_is_running(server.process_id):
                    # Collect any status information that may be needed (TODO ping websocket server)
                    server_obj = server.export()
                    # Add new keys to server object here before exporting 
                    online_servers.append(server_obj)
        return resp("SUCCESS_SERVER_STATUS_GET", {"servers": online_servers})
        
    else:
        return auth

@api_view(['DELETE'])
def view_kill(request, id):
    global server_processes
    auth = authenticate(request, [Superuser], [])
    if auth == True:
        match = Server.objects.filter(id=id)
        if not match:
            return responses.ERROR_RESOURCE_NOT_FOUND
        server = match[0]
        if server.process_id != "" and server.session != None:
            if process_is_running(server.process_id):
                server_processes[server.process_id].kill() 
        return resp("SUCCESS_SERVER_KILL", {})
    else:
        return auth
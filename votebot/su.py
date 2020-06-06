import argparse
import sys
import configparser
import requests
import json

parser = argparse.ArgumentParser()

action_choices = [
    "addsu",
    "delsu",
    "editsu",
    "su",
    "addhost",
    "delhost",
    "edithost",
    "hosts",
    "addsession",
    "delsession",
    "editsession",
    "sessions",
    "topics",
    "addtopic",
    "deltopic",
    "addvoter",
    "delvoter",
    "voters",
    "editvoter",
    "sv",
    "addsv",
    "remsv",
    "launch",
    "servers",
    "kill",
    "ping",
]

parser.add_argument("action", help="The VBSU action to run", choices=action_choices)
parser.add_argument("--id", help="Specifies an item ID", nargs=1)
parser.add_argument("--hid", help="Specifies a host ID", nargs=1)
parser.add_argument("-r", "--root", help="Run as Votebot root user", action="store_true")

args = parser.parse_args()

config = configparser.ConfigParser()
config.read("su.ini")

url = config["general"]["url"]

print()

if args.root:
    secret = config["root"]["secret"]
else:
    username = config["superuser"]["username"]
    password = config["superuser"]["password"]
    auth_response = requests.post(url + "/api/auth/superuser", data={"username": username, "password": password})
    response = auth_response.json()
    response_code = auth_response.status_code
    if response_code == 200:
        secret = response["superuser"]["secret"]
        print("Authentication successful. Secret key acquired.")
    else:
        print("Login unsuccessful (" + str(response_code) + ")")
        sys.exit(0)

print("Using secret: " + secret)
print()

if args.action == "addsu":
    request = {
        "username": input("Username: "),
        "password": input("Password: "),
        "first_name": input("First name: "),
        "last_name": input("Last name: ")
    }
    response = requests.post(url + "/api/superusers?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Superuser created")
    elif response.status_code == 400:
        resp = response.json()
        for err in resp["errors"]:
            print(err + ":" + resp["errors"][err][0])

elif args.action == "delsu":
    username = input("Username to delete: ")
    response = requests.delete(url + "/api/superusers/" + username + "?secret=" + secret)
    if response.status_code == 200:
        print("Superuser deleted")
    elif response.status_code == 404:
        print("Superuser not found")

elif args.action == "editsu":
    username = input("Username to edit: ")
    request = {
        "password": input("New password: "),
        "first_name": input("New first name: "),
        "last_name": input("New last name: ")
    }
    response = requests.put(url + "/api/superusers/" + username + "?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Superuser updated")
    elif response.status_code == 404:
        print("Superuser not found")

elif args.action == "su":
    if args.id:
        response = requests.get(url + "/api/superusers/" + args.id[0] + "?secret=" + secret)
        if response.status_code == 200:
            data = response.json()
            print("Showing details for superuser " + args.id[0] + ":")
            print("  - " + data["superuser"]["username"] + " (" + data["superuser"]["first_name"] + " " + data["superuser"]["last_name"] + ")")
        elif response.status_code == 404:
            print("Superuser not found")
    else:
        response = requests.get(url + "/api/superusers?secret=" + secret)
        if response.status_code == 200:
            data = response.json()
            print("Showing all superusers:")
            for person in data["superusers"]:
                print("  - " + person["username"] + " (" + person["first_name"] + " " + person["last_name"] + ")")

elif args.action == "addhost":
    request = {
        "username": input("Username: "),
        "password": input("Password: "),
        "name": input("Name: "),
        "max_voters": input("Maximum registered voters: "),
        "contact_name": input("Contact's name: "),
        "contact_email": input("Contact's email: "),
        "contact_phone": input("Contact's phone #: "),
        "server_port": input("New dedicated server port: "),
    }
    response = requests.post(url + "/api/hosts?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Host created")
    elif response.status_code == 400:
        resp = response.json()
        for err in resp["errors"]:
            print(err + ":" + resp["errors"][err][0])

elif args.action == "delhost":
    username = input("Username to delete: ")
    response = requests.delete(url + "/api/hosts/" + username + "?secret=" + secret)
    if response.status_code == 200:
        print("Host deleted")
    elif response.status_code == 404:
        print("Host not found")

elif args.action == "edithost":
    username = input("Username to edit: ")
    request = {
        "password": input("Password: "),
        "name": input("Name: "),
        "max_voters": input("Maximum registered voters: "),
        "contact_name": input("Contact's name: "),
        "contact_email": input("Contact's email: "),
        "contact_phone": input("Contact's phone #: "),
    }
    response = requests.put(url + "/api/hosts/" + username + "?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Host updated")
    elif response.status_code == 404:
        print("Host not found")

elif args.action == "hosts":
    if args.id:
        response = requests.get(url + "/api/hosts/" + args.id[0] + "?secret=" + secret)
        if response.status_code == 200:
            data = response.json()
            print("Showing details for host " + args.id[0] + ":")
            print("  - Username: " + data["host"]["username"])
            print("  - Name: " + data["host"]["name"])
            print("  - Maximum registered voters: " + str(data["host"]["max_voters"]))
            print("  - Contact's name: " + data["host"]["contact_name"])
            print("  - Contact's email: " + data["host"]["contact_email"])
            print("  - Contact's phone #: " + data["host"]["contact_phone"])
        elif response.status_code == 404:
            print("Host not found")
    else:
        response = requests.get(url + "/api/hosts?secret=" + secret)
        if response.status_code == 200:
            data = response.json()
            print("Listing all hosts:")
            for host in data["hosts"]:
                print("  - " + host["username"] + " (" + host["name"] + ")")

elif args.action == "addsession":
    host = input("Host name to add to: ")
    request = {
        "name": input("Session name: "),
        "send_voter_stats": input("Voters can see results (True/False): "),
        "hide_voters": input("Voter identities are hidden (True/False): "),
    }
    response = requests.post(url + "/api/hosts/" + host + "/sessions?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Session created (ID: " + response.json()["session"]["id"] + ")")
    elif response.status_code == 400:
        resp = response.json()
        for err in resp["errors"]:
            print(err + ":" + resp["errors"][err][0])

elif args.action == "sessions":
    if args.hid:
        response = requests.get(url + "/api/hosts/" + args.hid[0] + "/sessions?secret=" + secret)
        if response.status_code == 200:
            data = response.json()
            print("Showing all sessions for host " + args.hid[0] + ":")
            for session in data["sessions"]:
                print("  - " + session["name"] + " (" + session["id"] + ")")
        elif response.status_code == 404:
            print("Host not found")
    elif args.id:
        response = requests.get(url + "/api/sessions/" + args.id[0] + "?secret=" + secret)
        if response.status_code == 200:
            data = response.json()
            print("Showing details for session " + args.id[0] + ":")
            session = data["session"]
            print("  - Name: " + session["name"])
            print("  - Owner: " + session["host"])
            print("  - Topics: " + str(len(session["topics"])))
            print("  - Voters: " + str(len(session["voters"])))
            print("  - Voters can see results: " + session["send_voter_stats"])
            print("  - Voter identities are hidden: " + session["hide_voters"])
            print("  - Observer key: " + session["observer_key"])

        elif response.status_code == 404:
            print("Session not found")
    else:
        print("You must specify a session ID or host ID")

elif args.action == "delsession":
    id = input("Session ID to delete: ")
    response = requests.delete(url + "/api/sessions/" + id + "?secret=" + secret)
    if response.status_code == 200:
        print("Session deleted")
    elif response.status_code == 404:
        print("Session not found")

elif args.action == "editsession":
    id = input("Session ID to edit: ")
    request = {
        "name": input("Updated session name: "),
        "send_voter_stats": input("Voters can see results (True/False): "),
        "hide_voters": input("Voter identities are hidden (True/False): "),
    }
    response = requests.put(url + "/api/sessions/" + id + "?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Session updated (" + id + ")")
    elif response.status_code == 404:
        print("Session not found")

elif args.action == "topics":
    session_id = input("Session ID: ")
    response = requests.get(url + "/api/sessions/" + session_id + "/topics?secret=" + secret)
    if response.status_code == 200:
        data = response.json()
        print("Showing all topics for session " + session_id + ":")
        for topic in data["topics"]:
            print("  - " + topic["text"] + " (" + topic["id"] + ")")
            for option in topic["options"]:
                print("    => " + option)
    elif response.status_code == 404:
        print("Session not found")

elif args.action == "addtopic":
    session_id = input("Session ID to add to: ")
    request = {
        "text": input("Topic text: "),
        "options": []
    }
    x = input("Enter topic option (empty line when done): ")
    while x != "":
        request["options"].append(x)
        x = input("Next option: ")

    response = requests.post(url + "/api/sessions/" + session_id + "/topics?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Topic created (ID: " + response.json()["topic"]["id"] + ")")
    elif response.status_code == 400:
        resp = response.json()
        for err in resp["errors"]:
            print(err + ":" + resp["errors"][err][0])
    elif response.status_code == 404:
        print("Session not found")

elif args.action == "deltopic":
    session_id = input("Session ID to delete from: ")
    id = input("Topic ID to delete: ")
    response = requests.delete(url + "/api/sessions/" + session_id + "/topics/" + id + "?secret=" + secret)
    if response.status_code == 200:
        print("Topic deleted")
    elif response.status_code == 404:
        print("Session or topic not found")

elif args.action == "addvoter":
    host_id = input("Host name to add to: ")
    request = {
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "email": input("Email: "),
    }
    response = requests.post(url + "/api/hosts/" + host_id + "/voters?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Voter created (ID: " + response.json()["voter"]["id"] + ")")
    elif response.status_code == 400:
        resp = response.json()
        for err in resp["errors"]:
            print(err + ":" + resp["errors"][err][0])
    elif response.status_code == 404:
        print("Host not found")

elif args.action == "voters":
    host = input("Host name to search: ")
    response = requests.get(url + "/api/hosts/" + host + "/voters?secret=" + secret)
    if response.status_code == 200:
        data = response.json()
        print("Showing all voters for host " + host + ":")
        for voter in data["voters"]:
            print("  - " + voter["first_name"] + " " + voter["last_name"] + " (" + voter["email"] + ") (" + voter["id"] + ")")
    elif response.status_code == 404:
        print("Host not found")

elif args.action == "delvoter":
    id = input("Voter ID to delete: ")
    response = requests.delete(url + "/api/voters/" + id + "?secret=" + secret)
    if response.status_code == 200:
        print("Voter deleted")
    elif response.status_code == 404:
        print("Voter not found")

elif args.action == "editvoter":
    id = input("Voter ID to edit: ")
    request = {
        "first_name": input("First name: "),
        "last_name": input("Last name: "),
        "email": input("Email: "),
    }
    response = requests.put(url + "/api/voters/" + id + "?secret=" + secret, data=request)
    if response.status_code == 200:
        print("Voter updated")
    elif response.status_code == 404:
        print("Voter not found")

elif args.action == "sv":
    id = input("Session ID to search: ")
    response = requests.get(url + "/api/sessions/" + id + "/voters?secret=" + secret)
    if response.status_code == 200:
        data = response.json()
        print("Showing all registered voters in session " + id + ":")
        for voter in data["voters"]:
            print("  - " + voter["first_name"] + " " + voter["last_name"] + " (" + voter["email"] + ") (" + voter["id"] + ")")
    elif response.status_code == 404:
        print("Session not found")
    
elif args.action == "addsv":
    id = input("Session ID to add to: ")
    vid = input("Voter ID to add: ")
    response = requests.post(url + "/api/sessions/" + id + "/voters?secret=" + secret, data={"voter_id": vid})
    if response.status_code == 200:
        data = response.json()
        name = data["voter"]["first_name"] + " " + data["voter"]["last_name"]
        print("Added " + name + " (" + vid + ") to session " + id)
    elif response.status_code == 404:
        print("Session or voter not found")

elif args.action == "remsv":
    id = input("Session ID to remove from: ")
    vid = input("Voter ID to remove: ")
    response = requests.delete(url + "/api/sessions/" + id + "/voters?secret=" + secret, data={"voter_id": vid})
    if response.status_code == 200:
        data = response.json()
        name = data["voter"]["first_name"] + " " + data["voter"]["last_name"]
        print("Removed " + name + " (" + vid + ") from session " + id)
    elif response.status_code == 404:
        print("Session or voter not found")

elif args.action == "launch":
    id = input("Session ID to launch: ")
    response = requests.post(url + "/api/servers/launch/" + id + "?secret=" + secret)
    if response.status_code == 200:
        print("Attempting to launch votebot websocket server. You can try to check the server's status with the 'ping' command.")
    elif response.status_code == 404:
        print("Session not found")
    elif response.status_code == 503:
        print("Cannot start: Server resource is busy")

elif args.action == "servers":
    response = requests.get(url + "/api/servers?secret=" + secret)
    if response.status_code == 200:
        data = response.json()
        if len(data["servers"]) == 0:
            print("There are no voting servers running right now.")
        else:
            print("Showing status of all running servers:")
            for server in data["servers"]:
                print("  - PORT " + str(server["port"]) + " (ID: " + server["id"] + ") - running session " + server["session"] + " (hosted by " + server["owner"] + ")")

elif args.action == "kill":
    id = input("Server ID to kill: ")
    response = requests.delete(url + "/api/servers/kill/" + id + "?secret=" + secret)
    if response.status_code == 200:
        print("Server has been forcefully killed")
    elif response.status_code == 404:
        print("Server not found")

elif args.action == "ping":
    print("This feature is not ready yet.")

print()
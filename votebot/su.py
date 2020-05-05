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
    "hosts"
]

parser.add_argument("action", help="The VBSU action to run", choices=action_choices)
parser.add_argument("--id", help="Specifies an item ID", nargs=1)
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

print()
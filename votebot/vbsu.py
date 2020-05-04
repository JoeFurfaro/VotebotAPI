import argparse
import sys
import configparser
import requests
import json

config = configparser.ConfigParser()
config.read("vbsu.ini")

url = config["superuser"]["url"]
username = config["superuser"]["username"]
password = config["superuser"]["password"]

auth_response = requests.post(url + "/api/auth/superuser", data={"username": username, "password": password})
response = auth_response.json()
response_code = auth_response.status_code

if response_code == 200:
    secret = response["superuser"]["secret"]
    print(secret)
    print("Authentication successful. Secret key acquired.")
else:
    print("Login unsuccessful (" + str(response_code) + ")")
    sys.exit(0)

parser = argparse.ArgumentParser()

action_choices = [
    "addsu",
    "delsu"
]

# parser.add_argument("-q", "--quiet", help="Silences program output", action="store_true")
# parser.add_argument("-a", "--add", help="Object adding mode", action="store_true")
# parser.add_argument("-r", "--remove", help="Object removing mode", action="store_true")
# parser.add_argument("-l", "--list", help="List object mode", action="store_true")
# parser.add_argument("-e", "--edit", help="Object editing mode", nargs="*")
# parser.add_argument("-g", "--group", help="Identifies the name of a group", nargs=1)
# parser.add_argument("-u", "--user", help="Identifies the name of a user", nargs=1)
# parser.add_argument("-p", "--permplug", help="Identifies a permissions string or a plugin name", nargs=1)

parser.add_argument("action", help="The VBSU action to run", choices=action_choices)
parser.add_argument("-u", "--user", help="Identifies the name of a super user", nargs=1)

args = parser.parse_args()
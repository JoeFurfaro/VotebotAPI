"""
This plugin implements core features of the RDK
"""
from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler
from wssb import config
from wssb import users

class RDKPlugin(plugins.WSSBPlugin):

    def __init__(self, quiet):

        PLUGIN_NAME = "rdk"
        PLUGIN_VERSION = "3.0.0"
        PLUGIN_AUTHOR = "Joe Furfaro"
        DEPENDENCIES = ["passwords"]

        super().__init__(PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, DEPENDENCIES, quiet)

        self.setup_handlers()

    def setup_handlers(self):
        event_handlers = [
            EventHandler(Events.SERVER_START, self.on_start),
        ]
        self.register_handlers(event_handlers)

    def process_command(self, args):
        self.on_start(None)

        if args[0] == "addu":
            if len(args) == 4:
                name = args[2]
                if users.add_user(name):
                    passwords = plugins.find("passwords")
                    passwords.on_start(None)
                    passwords.passwords_config.set(name, "password", args[3])
                    passwords.passwords_config.save()
                    user_type = args[1]
                    if user_type == "robot":
                        users.add_user_to_group(name, "robot")
                        users.add_user_to_group(name, "robot_manager")
                    elif user_type == "operator":
                        users.add_user_to_group(name, "operator")
                    elif user_type == "observer":
                        users.add_user_to_group(name, "observer")
                    elif user_type == "developer":
                        users.add_user_to_group(name, "developer")
                    elif user_type == "admin":
                        users.add_user_to_group(name, "operator")
                        users.add_user_to_group(name, "observer")
                        users.add_user_to_group(name, "developer")
                    self.info("Added '" + name + "'")
                else:
                    self.error("Could not add to user list")
            else:
                self.error("Invalid syntax. Try: add [robot|operator|observer|developer|admin] [name] [private key]")

        elif args[0] == "delu":
            if len(args) == 2:
                name = args[1]
                if users.remove_user(name):
                    self.info("Deleted '" + name + "'")
                else:
                    self.error("'" + name + "' does not exist")

            else:
                self.error("Invalid syntax. Try: del [name]")

        else:
            self.error("Command not found")

    def on_start(self, context):
        if context != None:
            self.info("RDK v" + self.version_str + " development server plugin loaded successfully")
        return True
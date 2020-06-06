from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler
from wssb import config
from wssb import users

class VotebotPlugin(plugins.WSSBPlugin):

    def __init__(self, quiet):

        PLUGIN_NAME = "votebot"
        PLUGIN_VERSION = "2.0.0"
        PLUGIN_AUTHOR = "Joe Furfaro"
        DEPENDENCIES = []

        super().__init__(PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, DEPENDENCIES, quiet)

        self.setup_handlers()

    def setup_handlers(self):
        event_handlers = [
            EventHandler(Events.SERVER_START, self.on_start),

        ]
        self.register_handlers(event_handlers)

    def on_start(self, context):

        default_config = {
            "GENERAL": {
                "voting_session_id": "",
                "api_auth_key": "",
            }
        }

        self.config = config.Config(self.path + "votebot.ini", default_config)
        self.config.autogen()

        if self.config["GENERAL"]["api_auth_key"] == "":
            self.error("FATAL: An API authentication key was not provided.")
            return False

        if self.config["GENERAL"]["voting_session_id"] == "":
            self.error("FATAL: A voting session ID to run was not specified. Server will not start.")
            return False

        if context != None:
            self.info("Passwords loaded successully")

        return True

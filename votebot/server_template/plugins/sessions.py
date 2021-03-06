"""
This plugin implements user sessions and session continuity
"""
from wssb import plugins
from wssb.events import Events
from wssb.events import EventHandler
from wssb import config
from wssb import users
from wssb.views import Target

import uuid
import asyncio

class Session():
    def __init__(self, user, keep_alive, sessions_plugin, socket=None):
        self.user = user
        self.id = str(uuid.uuid4())
        self.keep_alive = keep_alive
        self.socket = socket
        self.sessions_plugin = sessions_plugin
        self.cancel_task = asyncio.create_task(self.clean_expired())

    async def clean_expired(self):
        await asyncio.sleep(self.keep_alive)
        self.sessions_plugin.sessions.remove(self)

    def refresh(self):
        self.cancel_task.cancel()
        self.cancel_task = asyncio.create_task(self.clean_expired())

class SessionsPlugin(plugins.WSSBPlugin):
    def __init__(self, quiet):

        PLUGIN_NAME = "sessions"
        PLUGIN_VERSION = "1.0.0"
        PLUGIN_AUTHOR = "Joe Furfaro"
        DEPENDENCIES = []

        super().__init__(PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR, DEPENDENCIES, quiet)

        self.setup_handlers()

    def new(self, user, keep_alive, socket=None):
        return Session(user, keep_alive, self, socket)

    def exists(self, session_id):
        return self.find(session_id) != None

    def is_valid(self, session_id):
        return self.exists(session_id)

    def find(self, session_id):
        for session in self.sessions:
            if session.id == session_id:
                return session
        return None

    def setup_handlers(self):
        event_handlers = [
            EventHandler(Events.SERVER_START, self.on_start),
            EventHandler(Events.USER_AUTH_ATTEMPT, self.on_auth_attempt),
            EventHandler(Events.USER_AUTHENTICATED, self.on_auth),
        ]
        self.register_handlers(event_handlers)

    def on_start(self, context):
        if context != None:
            self.info("Sessions loaded successully")

        default_config = {
            "Options": {
                "session_timeout": "300",
            }
        }

        self.config = config.Config(self.path + "sessions.ini", default_config)
        self.config.autogen()

        self.sessions = set()
        self.not_new = set()

        return True

    def on_auth_attempt(self, context):
        user = context["user"]
        request = context["request"]
        socket = context["socket"]

        if "session_id" in request:
            session = self.find(request["session_id"])
            if session != None and self.is_valid(session.id):
                self.not_new.add(socket)
                return True
            return False
        return True

    def on_auth(self, context):
        user = context["user"]
        socket = context["socket"]

        if socket not in self.not_new:
            new_session = self.new(user, int(self.config["Options"]["session_timeout"]), socket)
            self.sessions.add(new_session)
            return self.resp({ "type": "response", "status": "info", "code": "SESSIONS_NEW", "session_id": new_session.id, "user_name": user.name }, Target.source())
        return None

    def on_disconnect(self, context):
        user = context["user"]
        socket = context["socket"]
        for session in self.sessions:
            if session.socket == socket:
                session.socket = None

from django.db import models

from django.core.validators import MinLengthValidator

class Superuser(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    secret = models.CharField(max_length=300)

    def export(self, include_secret=False):
        exp = {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
        if include_secret:
            exp["secret"] = self.secret

        return exp

class Host(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=50)
    voters = models.ManyToManyField("Voter")
    max_voters = models.IntegerField()
    password = models.CharField(max_length=50)
    secret = models.CharField(max_length=300)
    contact_name = models.CharField(max_length=50)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50)
    voting_server = models.ForeignKey("Server", on_delete=models.CASCADE, null=True)
    results = models.ManyToManyField("Results")

    def export(self, include_secret=False):
        exp = {
            "username": self.username,
            "name": self.name,
            "max_voters": self.max_voters,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
        }
        if include_secret:
            exp["secret"] = self.secret

        return exp

    def export_session_details(self):
        sessions = Session.objects.filter(host=self)
        exp = []
        for session in sessions:
            exp.append({
                "id": session.id,
                "name": session.name,
            })
        return exp


class Voter(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    secret = models.CharField(max_length=64)
    parent_host = models.ForeignKey("Host", on_delete=models.CASCADE, null=True)

    def export(self, include_secret=False):
        exp = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "host": self.parent_host.username,
        }
        if include_secret:
            exp["secret"] = self.secret

        return exp

class Server(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    path = models.CharField(max_length=200)
    owner = models.ForeignKey("Host", on_delete=models.CASCADE)
    session = models.ForeignKey("Session", on_delete=models.SET_NULL, blank=True, null=True)
    process_id = models.CharField(max_length=20)
    port = models.IntegerField()

    def session_str(self):
        if self.session == None:
            return "None"
        return self.session.id

    def export(self):
        return {
            "id": self.id,
            "path": self.path,
            "owner": self.owner.username,
            "session": self.session_str(),
            "process_id": self.process_id,
            "port": self.port
        }

    def reset(self):
        self.session = None
        self.process_id = ""
        self.save()

class Session(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=200, validators=[MinLengthValidator(1)])
    host = models.ForeignKey("Host", on_delete=models.CASCADE, null=True)
    topics = models.ManyToManyField("Topic")
    voters = models.ManyToManyField("Voter")
    send_voter_stats = models.BooleanField()
    hide_voters = models.BooleanField()
    observer_key = models.CharField(max_length=300)
    date_created = models.DateField(auto_now_add=True)

    def export(self):
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host.username,
            "topics": [topic.export() for topic in self.topics.all()],
            "voters": [voter.export() for voter in self.voters.all()],
            "send_voter_stats": str(self.send_voter_stats),
            "hide_voters": str(self.hide_voters),
            "observer_key": self.observer_key
        }

class Results(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    session = models.ForeignKey("Session", on_delete=models.CASCADE)
    start_time = models.DateField()
    end_time = models.DateField()
    topic_results = models.ManyToManyField("TopicResults")

    def export(self):
        return {
            "id": self.id,
            "session": self.session.export(),
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "topic_results": self.topic_results.export()
        }

class Topic(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    text = models.TextField()
    options = models.ManyToManyField("Option")

    def export(self):
        return {
            "id": self.id,
            "text": self.text,
            "options": [option.text for option in self.options.all()]
        }

class TopicResults(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)
    votes = models.ManyToManyField("Vote")

    def export(self):
        return {
            "id": self.id,
            "topic": self.topic.export(),
            "votes": [vote.export() for vote in self.votes.all()]
        }

class Vote(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    voter = models.ForeignKey("Voter", on_delete=models.SET_NULL, blank=True, null=True)
    value = models.TextField()
    time_placed = models.DateField()

    def export(self):
        return {
            "id": self.id,
            "voter": self.voter.export(),
            "value": self.value,
            "time_placed": str(self.time_placed)
        }

class Option(models.Model):
    text = models.TextField()
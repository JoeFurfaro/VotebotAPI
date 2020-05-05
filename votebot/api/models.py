from django.db import models

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


class Voter(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    secret = models.CharField(max_length=8)
    parent_host = models.ForeignKey("Host", on_delete=models.CASCADE)

class Server(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    path = models.CharField(max_length=200)
    owner = models.ForeignKey("Host", on_delete=models.CASCADE)
    session = models.ForeignKey("Session", on_delete=models.SET_NULL, blank=True, null=True)
    process_id = models.CharField(max_length=20)
    port = models.IntegerField()

class Session(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    host = models.ForeignKey("Host", on_delete=models.CASCADE)
    topics = models.ManyToManyField("Topic")
    voters = models.ManyToManyField("Voter")

class Results(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    session = models.ForeignKey("Session", on_delete=models.CASCADE)
    start_time = models.DateField()
    end_time = models.DateField()
    topic_results = models.ManyToManyField("TopicResults")

class Topic(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    text = models.TextField()
    options = models.ManyToManyField("Option")

class TopicResults(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)
    votes = models.ManyToManyField("Vote")

class Vote(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    voter = models.ForeignKey("Voter", on_delete=models.SET_NULL, blank=True, null=True)
    value = models.TextField()
    time_placed = models.DateField()

class Option(models.Model):
    text = models.TextField()
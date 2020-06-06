from api.models import *
from rest_framework import serializers

# from api.views import generate_secret

import uuid

class SuperuserPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Superuser
        fields = ['username', 'first_name', 'last_name', 'password']

class SuperuserPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Superuser
        fields = ['first_name', 'last_name', 'password']

class TopicSerializer(serializers.ModelSerializer):
    options = serializers.ListField(child=serializers.CharField(), required=True)

    class Meta:
        model = Topic
        fields = ['text', 'options']

    def create(self, validated_data):
        topic = Topic.objects.create(id=str(uuid.uuid4()), text=validated_data["text"])
        for option in validated_data["options"]:
            topic.options.add(Option.objects.create(text=option))
        topic.save()
        return topic

class VoterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voter
        fields = ['first_name', 'last_name', 'email']

    def create(self, validated_data):
        voter = Voter.objects.create(
            id=str(uuid.uuid4()),
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        return voter

class HostPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['username', 'password', 'name', 'max_voters', 'contact_name', 'contact_email', 'contact_phone']

class HostPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['password', 'name', 'max_voters', 'contact_name', 'contact_email', 'contact_phone']

class SessionSerializer(serializers.ModelSerializer):
    send_voter_stats = serializers.BooleanField(required=True)
    hide_voters = serializers.BooleanField(required=True)

    class Meta:
        model = Session
        fields = ['name', 'send_voter_stats', 'hide_voters']

    def create(self, validated_data):
        name = validated_data["name"]
        send_voter_stats = bool(validated_data["send_voter_stats"])
        session = Session.objects.create(id=str(uuid.uuid4()), name=name, send_voter_stats=send_voter_stats, hide_voters=validated_data["hide_voters"])
        return session
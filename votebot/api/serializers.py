from api.models import *
from rest_framework import serializers

class SuperuserPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Superuser
        fields = ['username', 'first_name', 'last_name', 'password']

class SuperuserPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Superuser
        fields = ['first_name', 'last_name', 'password']

class HostPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['username', 'password', 'name', 'max_voters', 'contact_name', 'contact_email', 'contact_phone']

class HostPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['password', 'name', 'max_voters', 'contact_name', 'contact_email', 'contact_phone']
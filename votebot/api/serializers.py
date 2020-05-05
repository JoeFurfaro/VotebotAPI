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
from api.models import *
from rest_framework import serializers

class SuperuserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Superuser
        fields = ['first_name', 'last_name', 'username']
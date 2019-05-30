from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'user_ip', 'user_code', 'date_creation', 'is_developer')


class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = '__all__'


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'


class AppRetentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'

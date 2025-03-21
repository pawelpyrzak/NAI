from django.utils.timesince import timesince
from rest_framework import serializers

from .models import Task, Event, Notification


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def get_relative_time(self, obj):
        return f"{timesince(obj.created_at)} temu"

from rest_framework import serializers
from .models import Machine, Event, Command, Heartbeat
import json

class MachineSerializer(serializers.ModelSerializer):
    ports = serializers.SerializerMethodField()
    vulns = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = '__all__'

    def get_ports(self, obj):
        return json.loads(obj.ports)

    def get_vulns(self, obj):
        return json.loads(obj.vulns)

class EventSerializer(serializers.ModelSerializer):
    raw_data = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_raw_data(self, obj):
        return json.loads(obj.raw_data)

class CommandSerializer(serializers.ModelSerializer):
    params = serializers.SerializerMethodField()

    class Meta:
        model = Command
        fields = '__all__'

    def get_params(self, obj):
        return json.loads(obj.params)

class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heartbeat
        fields = '__all__'

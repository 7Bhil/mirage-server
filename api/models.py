from django.db import models
import json

class Machine(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    hostname = models.CharField(max_length=255, default="Unknown")
    last_seen = models.DateTimeField(auto_now=True)
    ports = models.TextField(default="[]") # JSON list
    vulns = models.TextField(default="[]") # JSON list
    status = models.CharField(max_length=50, default="Healthy")
    score = models.IntegerField(default=100)

    def set_ports(self, ports_list):
        self.ports = json.dumps(ports_list)

    def get_ports(self):
        return json.loads(self.ports)

    def __str__(self):
        return f"{self.hostname} ({self.ip})"

class Event(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)
    component = models.CharField(max_length=50)
    event_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    ip = models.GenericIPAddressField(null=True, blank=True)
    description = models.TextField()
    raw_data = models.TextField(default="{}") # JSON

    def __str__(self):
        return f"[{self.severity}] {self.component} - {self.description[:50]}"

class Command(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('executed', 'Executed'),
        ('failed', 'Failed'),
    ]
    component = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    target_ip = models.GenericIPAddressField(null=True, blank=True)
    params = models.TextField(default="{}") # JSON
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    result = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} on {self.target_ip} ({self.status})"

class Heartbeat(models.Model):
    component = models.CharField(max_length=50, primary_key=True)
    last_seen = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default="online")

    def __str__(self):
        return f"{self.component} - {self.status}"

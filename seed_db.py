import os
import django
import json
from datetime import datetime

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mirage_server.settings')
django.setup()

from api.models import Machine, Event, Heartbeat

def populate():
    print("🚀 Peuplement de la base de données MIRAGE...")

    # 1. Machines
    machines_data = [
        {"ip": "10.58.76.1", "hostname": "Gateway-Cisco", "status": "Healthy", "score": 100, "ports": [80, 443]},
        {"ip": "10.58.76.115", "hostname": "Bhil-Workstation", "status": "Warning", "score": 85, "ports": [22, 80, 3306], "vulns": ["CVE-2023-1234"]},
        {"ip": "10.58.76.200", "hostname": "Server-Prod-01", "status": "Healthy", "score": 98, "ports": [80, 443, 8080]},
    ]

    for m in machines_data:
        obj, created = Machine.objects.update_or_create(
            ip=m["ip"],
            defaults={
                "hostname": m["hostname"],
                "status": m["status"],
                "score": m["score"],
                "ports": json.dumps(m.get("ports", [])),
                "vulns": json.dumps(m.get("vulns", [])),
            }
        )
        print(f"  - Machine {m['ip']} {'créée' if created else 'mise à jour'}")

    # 2. Events
    events_data = [
        {"component": "SCAN", "event_type": "discovery", "severity": "info", "ip": "10.58.76.115", "description": "Nouvel appareil détecté sur le réseau."},
        {"component": "SENTINELLE", "event_type": "intrusion", "severity": "critical", "ip": "192.168.1.50", "description": "Tentative de force brute SSH détectée !"},
        {"component": "ORACLE", "event_type": "automation", "severity": "info", "ip": "10.58.76.200", "description": "Déploiement automatique d'un leurre GHOST."},
        {"component": "GHOST", "event_type": "interaction", "severity": "warning", "ip": "192.168.1.50", "description": "L'attaquant a mordu à l'hameçon sur le port 22."},
    ]

    for e in events_data:
        Event.objects.create(**e)
    print(f"  - {len(events_data)} événements ajoutés")

    # 3. Heartbeats
    components = ["SCAN", "SENTINELLE", "GHOST", "ORACLE", "TRACE"]
    for comp in components:
        Heartbeat.objects.update_or_create(
            component=comp,
            defaults={"status": "online"}
        )
    print("  - Piliers activés (Heartbeats)")

    print("✅ Terminé !")

if __name__ == "__main__":
    populate()

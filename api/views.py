from rest_framework import status, viewsets
from rest_framework.response import Response

from .mirage_db import get_mirage_db
from .models import Machine, Event, Command, Heartbeat
from .serializers import MachineSerializer, EventSerializer, CommandSerializer, HeartbeatSerializer


def _machine_to_api(m):
    return {
        "ip": m["ip"],
        "hostname": m.get("hostname", "Unknown"),
        "last_seen": m.get("last_seen"),
        "ports": m.get("ports", []),
        "vulns": m.get("vulns", []),
        "status": m.get("status", "Healthy"),
        "score": m.get("score", 100),
    }


def _event_to_api(e):
    return {
        "id": e.get("event_id"),
        "timestamp": e.get("timestamp"),
        "component": (e.get("component") or "").upper(),
        "event_type": e.get("type", "info"),
        "severity": e.get("severity", "info"),
        "ip": e.get("ip") or e.get("target", {}).get("ip"),
        "description": e.get("message")
        or e.get("description")
        or e.get("data", {}).get("description", ""),
        "raw_data": e,
    }


def _heartbeat_to_api(name, hb):
    return {
        "component": name.upper(),
        "last_seen": hb.get("last_seen"),
        "status": hb.get("status", "online"),
    }


def _command_to_api(c):
    return {
        "id": c.get("_id"),
        "component": (c.get("component") or "").upper(),
        "action": c.get("action"),
        "target_ip": c.get("target_ip"),
        "params": c.get("params", {}),
        "status": "pending",
        "timestamp": c.get("timestamp"),
        "result": None,
    }


class MachineViewSet(viewsets.ViewSet):
    """Machines — source : mirage_core.db"""

    def list(self, request):
        db = get_mirage_db()
        data = [_machine_to_api(m) for m in db.get_all_machines()]
        if not data:
            data = MachineSerializer(Machine.objects.all(), many=True).data
        return Response(data)

    def retrieve(self, request, pk=None):
        machines = [_machine_to_api(m) for m in get_mirage_db().get_all_machines()]
        for m in machines:
            if m["ip"] == pk:
                return Response(m)
        try:
            obj = Machine.objects.get(pk=pk)
            return Response(MachineSerializer(obj).data)
        except Machine.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        db = get_mirage_db()
        db.update_machine(request.data)
        return Response(_machine_to_api(request.data), status=status.HTTP_201_CREATED)


class EventViewSet(viewsets.ViewSet):
    def list(self, request):
        db = get_mirage_db()
        events = [_event_to_api(e) for e in db.get_latest_events(100)]
        if not events:
            events = EventSerializer(Event.objects.all().order_by("-timestamp")[:100], many=True).data
        return Response(events)

    def create(self, request):
        db = get_mirage_db()
        payload = dict(request.data)
        if "event_type" in payload and "type" not in payload:
            payload["type"] = payload.pop("event_type")
        if "description" in payload and "data" not in payload:
            payload.setdefault("data", {})["description"] = payload["description"]
        db.insert_event(payload)
        return Response(_event_to_api(payload), status=status.HTTP_201_CREATED)


class CommandViewSet(viewsets.ViewSet):
    def list(self, request):
        db = get_mirage_db()
        commands = []
        for comp in ("SCAN", "SENTINELLE", "GHOST", "ORACLE", "TRACE"):
            commands.extend(_command_to_api(c) for c in db.get_pending_commands(comp))
        if not commands:
            commands = CommandSerializer(Command.objects.all().order_by("-timestamp")[:50], many=True).data
        return Response(commands)

    def create(self, request):
        db = get_mirage_db()
        data = request.data
        component = data.get("component", "SCAN")
        action = data.get("action", "discovery")
        target_ip = data.get("target_ip")
        params = data.get("params", {})
        if isinstance(params, str):
            import json
            try:
                params = json.loads(params) if params else {}
            except json.JSONDecodeError:
                params = {}
        cmd_id = db.push_command(component, action, target_ip=target_ip, params=params)
        out = {
            "id": cmd_id,
            "component": component.upper(),
            "action": action,
            "target_ip": target_ip,
            "params": params,
            "status": "pending",
        }
        return Response(out, status=status.HTTP_201_CREATED)


class HeartbeatViewSet(viewsets.ViewSet):
    def list(self, request):
        hb_map = get_mirage_db().get_heartbeats()
        data = [_heartbeat_to_api(k, v) for k, v in hb_map.items()]
        if not data:
            data = HeartbeatSerializer(Heartbeat.objects.all(), many=True).data
        return Response(data)

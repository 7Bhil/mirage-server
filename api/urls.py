from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MachineViewSet, EventViewSet, CommandViewSet, HeartbeatViewSet

router = DefaultRouter()
router.register(r'machines', MachineViewSet, basename='machine')
router.register(r'events', EventViewSet, basename='event')
router.register(r'commands', CommandViewSet, basename='command')
router.register(r'heartbeats', HeartbeatViewSet, basename='heartbeat')

urlpatterns = [
    path('', include(router.urls)),
]

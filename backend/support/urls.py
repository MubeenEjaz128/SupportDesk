from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView, DashboardStatsView, CustomerViewSet, TicketViewSet, KnowledgeViewSet, ActivityListView, TeamViewSet

router = DefaultRouter()
router.register('customers', CustomerViewSet, basename='customer')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('knowledge', KnowledgeViewSet, basename='knowledge')
router.register('team', TeamViewSet, basename='team')
urlpatterns = [
    path('auth/me/', MeView.as_view()),
    path('dashboard/stats/', DashboardStatsView.as_view()),
    path('activity/', ActivityListView.as_view()),
    path('', include(router.urls)),
]

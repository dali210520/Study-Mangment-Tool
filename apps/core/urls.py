from django.urls import path

from .views import ApiInfoView, HealthCheckView
from . import views

urlpatterns = [
    path('', ApiInfoView.as_view(), name='api-root'),
    path('health/', HealthCheckView.as_view(), name='api-health'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('notifications/<int:pk>/delete/', views.delete_notification, name='delete-notification'),
]

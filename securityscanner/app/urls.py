from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_view, name='scan'),
    path('status/<str:job_id>/', views.status_view, name='status'),
    path('cors-test/', views.cors_test, name='cors_test'),
    path('health/', views.health_check, name='health'),
]

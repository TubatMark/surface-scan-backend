from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_view, name='scan'),
    path('status/<str:job_id>/', views.status_view, name='status'),
]

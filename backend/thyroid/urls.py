"""
URL routing for the Thyroid API.
"""

from django.urls import path
from .views import HealthCheckView, NoduleEvaluationView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('nodule/evaluate/', NoduleEvaluationView.as_view(), name='nodule-evaluate'),
]

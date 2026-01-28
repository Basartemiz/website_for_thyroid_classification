"""
URL configuration for Thyroid Nodule Evaluation System.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import TemplateView
from django.http import HttpResponse


def health_check_simple(request):
    """Simple health check for load balancer that doesn't need full API."""
    return HttpResponse("OK", content_type="text/plain")


# API routes
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('thyroid.urls')),
    path('health/', health_check_simple),  # Simple health check for LB
]

# In production, serve the SPA for all non-API routes.
# Static assets (/assets/*, /vite.svg) are served by WhiteNoise via WHITENOISE_ROOT.
# This catch-all serves index.html for client-side routing.
if not settings.DEBUG:
    frontend_index = settings.BASE_DIR / 'staticfiles' / 'frontend' / 'index.html'

    if frontend_index.exists():
        urlpatterns += [
            re_path(r'^(?!api/|admin/|static/|health/).*$', TemplateView.as_view(template_name='index.html')),
        ]

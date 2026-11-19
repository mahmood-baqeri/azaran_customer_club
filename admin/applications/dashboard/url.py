# Path: applications/dashboard/url.py

# applications/dashboard/urls.py

from django.urls import path
from .views import dashboard, report_export, report_view

app_name = "app_dashboard"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("reports/<str:report_type>/", report_view, name="report_view"),
    path("reports/<str:report_type>/export/", report_export, name="report_export"),
]
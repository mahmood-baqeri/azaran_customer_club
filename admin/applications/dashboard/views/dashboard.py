# applications/dashboard/views/dashboard.py

from django.shortcuts import render

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess

from ..repositories import (
    chart_factors_monthly,
    chart_orders_status,
    chart_projects_type,
    chart_promotion_orders_status,
    chart_scores_daily,
    chart_users_monthly,
    chart_users_nature,
    dashboard_kpis,
)


@is_admin_required
def dashboard(request):
#     RequiredAccess(request, "DashboardRead")

    kpis = dashboard_kpis()
    charts = {
        "users_monthly": chart_users_monthly(12),
        "orders_status": chart_orders_status(),
        "promotion_orders_status": chart_promotion_orders_status(),
        "projects_type": chart_projects_type(),
        "users_nature": chart_users_nature(),
        "scores_daily": chart_scores_daily(30),
        "factors_monthly": chart_factors_monthly(6),
    }

    data = {
        "pageTitle": "داشبورد",
        "kpis": kpis,
        "charts": charts,
    }
    return render(request, "pages/dashboard/index.html", {"data": data})
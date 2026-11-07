from datetime import datetime, timedelta
from pprint import pprint
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Avg, Count, Sum, Min, Max
from django_dump_die.middleware import dd

import jdatetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Case, When, IntegerField, DateField
from django.db.models.functions import TruncDate
import logging

from applications.core.decorators import is_admin_required


@is_admin_required
def dashboard(request):
    data = {}
    data["pageTitle"] = 'داشبورد'

    data['userScoreChart'] = []

  

    return render(request, "pages/dashboard.html", {"data": data})





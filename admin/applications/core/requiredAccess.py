from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from applications.core.processors import adminAccess


#  بررسی اجاز دسترسی مدیر به اکشن مورد نظر
def RequiredAccess(request, action):
    if action not in adminAccess(request)['adminAccess']:
        logout(request)
        raise PermissionDenied
    return True

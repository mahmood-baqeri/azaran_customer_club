import functools
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout


def is_admin_required(view_func, redirect_url="app_user:admin_login_with_pass"):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect(redirect_url)

        if user.is_superuser != 1 or user.is_active != 1 or user.is_staff != 1:
            logout(request)
            return redirect(redirect_url)

        return view_func(request, *args, **kwargs)
    return wrapper


def authentication_required(view_func, redirect_url="page:index"):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("page:index")

        return view_func(request, *args, **kwargs)
    return wrapper


def authentication_not_required(view_func, redirect_url="accounts:profile"):
    """
        this decorator ensures that a user is not logged in,
        if a user is logged in, the user will get redirected to
        the url whose view name was passed to the redirect_url parameter
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        messages.info(request, "You need to be logged out")
        print("You need to be logged out")
        return redirect(redirect_url)

    return wrapper


def verification_required(view_func, verification_url="accounts:activate_email"):
    """
        this decorator restricts users who have not been verified
        from accessing the view function passed as it argument and
        redirect the user to page where their account can be activated
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_active:
            return view_func(request, *args, **kwargs)
        messages.info(request, "Email verification required")
        print("You need to be logged out")
        return redirect(verification_url)

    return wrapper


def xhr_request_only(view_func):
    """
    this decorators ensures that the view func accepts only
    XML HTTP Request i.e request done via fetch or ajax
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return view_func(request, *args, **kwargs)
        print("Can't Process this Request")
        return HttpResponseBadRequest("Can't Process this Request")

    return wrapper

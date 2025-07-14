from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return render(request, "permission_denied.html", status=403)

        return wrapper

    return decorator


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == "admin")(
        view_func
    )

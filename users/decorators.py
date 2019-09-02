from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from functools import wraps


def has_share(function):
    def wrap(request, *args, **kwargs):
        if request.user.profile.current_member:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def check_grouup(group_name):
    def _check_group(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name=group_name).exists():
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied

            return function(request, *args, **kwargs)

        return wrapper

    return _check_group

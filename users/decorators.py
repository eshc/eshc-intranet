from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from functools import wraps

from home.models import Role



def has_share(function):
    def wrap(request, *args, **kwargs):
        if request.user.profile.current_member:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def current_member_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.profile.current_member:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def check_role(function, role_name):
    def wrap(request, *args, **kwargs):
        if Role.objects.filter(assigned_to=request.user, role_name=role_name).exists():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# def check_group(function, group_name):
#     def wrap(request, *args, **kwargs):
#         print(Role.objects.filter(assigned_to=request.user, role_name=group_name))
#         if request.user.groups.filter(name=group_name).exists():
#             return function(request, *args, **kwargs)
#         else:
#             raise PermissionDenied

#     wrap.__doc__ = function.__doc__
#     wrap.__name__ = function.__name__
#     return wrap

# def check_role(role_name):
#     def _check_role(function):
#         @wraps(function)
#         def wrapper(request, *args, **kwargs):
#             if request.user.roles.filter(name=role_name).exists():
#                 return function(request, *args, **kwargs)
#             else:
#                 raise PermissionDenied

#             return function(request, *args, **kwargs)

#         return wrapper

#     return _check_role

# def check_group(group_name):
#     def _check_group(function):
#         @wraps(function)
#         def wrapper(request, *args, **kwargs):
#             if request.user.groups.filter(name=group_name).exists():
#                 return function(request, *args, **kwargs)
#             else:
#                 raise PermissionDenied

#             return function(request, *args, **kwargs)

#         return wrapper

#     return _check_group

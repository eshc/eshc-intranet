from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

def has_share(function):
	def wrap(request, *args, **kwargs):
		if request.user.profile.share_received:
			return function(request, *args, **kwargs)
		else:
			raise PermissionDenied
			
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap

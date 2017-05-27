from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import Lease 

@login_required
def inventory(request, pk):
	# lease = Lease.objects.get(pk=pk)
	lease = get_object_or_404(Lease, pk=pk)

	# Verify lease belongs to the user
	if request.user.id == lease.user_id:
		context = {'lease': lease}
	else:
		context = {'lease': 'You do not have permission to view this page.'}
	return render(request, 'leases/inventory.html', context)

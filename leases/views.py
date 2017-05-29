from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from .models import Lease, Inventory
from .forms import InventoryForm

@login_required
def inventory(request, pk):
	# lease = Lease.objects.get(pk=pk)
	lease = get_object_or_404(Lease, pk=pk)

	# Verify lease belongs to the user
	if request.user.id == lease.user_id:

		if request.method != 'POST':
			# Display empty form
			inventory_form = InventoryForm()
		else:
			inventory_form = InventoryForm(data=request.POST)#, instance=inventory)
			# inventory_form.sub_date = timezone.localdate()
			if inventory_form.is_valid():
				inventory_form = inventory_form.save()
				return HttpResponseRedirect(reverse('users:profile'))


		context = {'lease': lease, 'inventory_form': inventory_form}
		# return render(request, 'users/edit_profile.html', context)


	else:
		return HttpResponseRedirect(reverse('users:profile'))
	return render(request, 'leases/inventory.html', context)



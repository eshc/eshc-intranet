from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Lease, Inventory
from .forms import InventoryForm

from users.decorators import has_share

@login_required
@has_share
def inventory(request, pk):
	# lease = Lease.objects.get(pk=pk)
	lease = get_object_or_404(Lease, pk=pk)
	saved_inventory = False

	# Verify lease belongs to the user
	if request.user.id == lease.user_id:
		if request.method != 'POST':
			# Display empty form
			inventory_list = ['Bed', 'Mattress', 'Desk', 'Carpets', 'Window', 'Wardrobe/Clothes Rack', 'Shelves', 'Walls', 'Door, lock, closer', 'Light working', 'Sockets working', 'Radiator working']
			initial_string = ''.join((item + ': \n\n') for item in inventory_list)
			inventory_form = InventoryForm(initial={'inventory_notes': initial_string})

			if Inventory.objects.filter(lease_id=lease.id).exists():
				saved_inventory = Inventory.objects.filter(lease_id=lease.id)[0].inventory_notes
		else:
			inventory_form = InventoryForm(data=request.POST)
			if inventory_form.is_valid():
				inventory_form = inventory_form.save(lease_id=lease.id)
				return HttpResponseRedirect(reverse('profile'))

		context = {'lease': lease, 'inventory_form': inventory_form, 'saved_inventory': saved_inventory}
		# return render(request, 'users/edit_profile.html', context)


	else:
		return HttpResponseRedirect(reverse('profile'))
	return render(request, 'leases/inventory.html', context)



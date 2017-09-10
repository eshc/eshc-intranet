from django import forms
from .models import Inventory
from django.utils import timezone


class InventoryForm(forms.ModelForm):

	class Meta:
		model = Inventory
		fields = ['inventory_notes']

	def save(self, lease_id, commit=True):
		inventory = super(InventoryForm, self).save(commit=False)
		inventory.inventory_notes = self.cleaned_data['inventory_notes']
		# inventory.sub_date = timezone.localdate()		# django 1.11
		inventory.sub_date = timezone.now().date()		# django 1.10
		inventory.lease_id = lease_id

		if commit:
			inventory.save()
		return inventory


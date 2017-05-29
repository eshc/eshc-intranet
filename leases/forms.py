from django import forms
from .models import Inventory

class InventoryForm(forms.ModelForm):

	class Meta:
		model = Inventory
		fields = ['inventory_notes']

	def save(self, commit=True):
		inventory = super(InventoryForm, self).save(commit=False)
		inventory.inventory_notes = self.cleaned_data['inventory_notes']

		if commit:
			inventory.save()
		return inventory


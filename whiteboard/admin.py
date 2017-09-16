from django.contrib import admin

from .models import Note

class NoteAdmin(admin.ModelAdmin):
	list_display = ['text', 'pub_date', 'submitted_by']

admin.site.register(Note, NoteAdmin)

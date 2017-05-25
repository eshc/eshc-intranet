from django.contrib import admin

from .models import Lease

class LeaseAdmin(admin.ModelAdmin):
	list_display = ('start_date', 'end_date', 'lease_type')

# class QuestionAdmin(admin.ModelAdmin):
# 	fieldsets = [
# 		(None,					{'fields': ['question_text']}),
# 		('Date Information',	{'fields': ['pub_date'],
# 			'classes': ['collapse']}),
# 	]
# 	inlines = [ChoiceInline]
# 	list_display = ('question_text', 'pub_date', 'was_published_recently')
# 	list_filter = ['pub_date']
# 	search_fields = ['question_text']

admin.site.register(Lease, LeaseAdmin)

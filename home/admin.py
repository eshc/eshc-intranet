from django.contrib import admin

from .models import GM, Point, WgUpdate

class PointInline(admin.TabularInline):
	model = Point
	fieldsets = []
	extra = 1

class WgUpdateInline(admin.TabularInline):
	model = WgUpdate
	fieldsets = []
	extra = 1

class GMAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,		{'fields': ['number', 'date_conv']}),
		]
	inlines = [PointInline, WgUpdateInline]
	list_display = ('number','date_conv','discussions', 'proposals')

	# list_display = ('title', 'proposal')
	# list_filter = ['pub_date']
	# search_fields = ['question_text']

admin.site.register(GM, GMAdmin)

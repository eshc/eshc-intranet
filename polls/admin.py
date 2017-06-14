from django.contrib import admin

from .models import Choice, Question

class ChoiceInline(admin.TabularInline):
	model = Choice
	extra = 3

class QuestionAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,					{'fields': ['question_text']}),
		('Date Information',	{'fields': ['pub_date', 'close_date'],
			'classes': ['collapse']}),
	]
	inlines = [ChoiceInline]
	list_display = ('question_title', 'pub_date', 'close_date')
	list_filter = ['pub_date']
	search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)

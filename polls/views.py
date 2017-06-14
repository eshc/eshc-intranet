from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from datetime import date
import markdown

from .models import Question, Choice
from .forms import QuestionSubmitForm

@login_required
def index(request):
	# TODO: divide questions into open and past proposals

	# questions = Question.objects.all()
	past_questions = Question.objects.filter(close_date__lte=date.today())
	open_questions = Question.objects.filter(close_date__gte=date.today())

	context = {'past_questions': past_questions, 'open_questions': open_questions}
	return render(request, 'polls/index.html', context)

@login_required
def submit(request):
	if request.method != 'POST':
		form = QuestionSubmitForm()
	else:
		form = QuestionSubmitForm(data=request.POST)

		if form.is_valid():
			question = form.save(commit=False)
			question.submitted_by = request.user
			question.pub_date = date.today()
			question.save()
			return HttpResponseRedirect(reverse('polls:index'))

	context = {'form': form}
	return render(request, 'polls/submit.html', context)

@login_required
def detail(request, pk):
	question = get_object_or_404(Question, pk=pk)
	question.question_text = markdown.markdown(question.question_text)
	context = {'question': question}

	return render(request, 'polls/detail.html', context)


@login_required
def delete(request, pk):
	question = get_object_or_404(Question, pk=pk)
	context = {'question': question}

	if question.submitted_by.id != request.user.id:
		return HttpResponseRedirect(reverse('polls:index'))

	if request.method != 'POST':
		pass
	else:
		question.delete()
		return HttpResponseRedirect(reverse('polls:index'))
		

	return render(request, 'polls/delete.html', context)

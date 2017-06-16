from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from datetime import date
import markdown

from .models import Question, Choice, Vote
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
			Choice.objects.create(question=question, choice_text="No")
			Choice.objects.create(question=question, choice_text="Abstain")
			Choice.objects.create(question=question, choice_text="Yes")
			return HttpResponseRedirect(reverse('polls:index'))

	context = {'form': form}
	return render(request, 'polls/submit.html', context)

@login_required
def detail(request, pk):
	question = get_object_or_404(Question, pk=pk)
	# Render markdown
	question.question_text = markdown.markdown(question.question_text)

	# Checking if proposal is still open
	if question.close_date >= date.today():
		question_open = True
	else:
		question_open = False


	# Checking if user already cast a vote
	if not (Vote.objects.filter(user=request.user, question=question).__nonzero__()):
		messages.add_message(request, messages.INFO, 'You have not voted on this proposal.')
		# voted = 'You have not voted on this proposal yet.'

	else:
		v = Vote.objects.get(user=request.user, question=question)
		messages.add_message(request, messages.INFO, 'You have already voted {}'.format(v.choice.choice_text))
		# voted = 'You have already voted ' + v.choice.choice_text


	# Handle voting button clicking
	choices = question.choice_set.all()
	if (request.GET):
		choice_clicked = choices.filter(choice_text=list(request.GET.keys())[0])

		if (Vote.objects.filter(user=request.user, question=question).__nonzero__()):
			v = Vote.objects.get(user=request.user, question=question)
			messages.add_message(request, messages.WARNING, 'You have already cast a vote. You voted {}'.format(v.choice.choice_text))

		else:
			v, created = Vote.objects.get_or_create(choice=choice_clicked[0],
												user=request.user, 
												question=question)
			if created:
				messages.add_message(request, messages.SUCCESS, 'Thank you for voting!')
				# voted = 'Voted just now'


	# Count votes
	votes = {}
	for choice in choices:
		votes[choice.choice_text] = Vote.objects.filter(question=question, choice=choice).count()

	
	context = {'question': question, 
				'question_open': question_open, 
				'choices': choices,
				'votes': votes,
				}
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
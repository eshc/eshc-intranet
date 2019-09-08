from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from users.decorators import current_member_required

from datetime import date
import markdown

from .models import Question, Choice, Vote
from .forms import QuestionSubmitForm

@login_required
@current_member_required
def index(request):
	past_questions = Question.objects.filter(close_date__lt=date.today())
	open_questions = Question.objects.filter(close_date__gte=date.today())

	closed_questions = []

	for question in past_questions:
		vote_count = []
		for choice in Choice.objects.filter(question=question):
			vote_count.append([choice.choice_text, Vote.objects.filter(question=question).filter(choice=choice).count()])
		prepped_list = [question, vote_count]
		closed_questions.append(prepped_list)

	current_questions = []
	for question in open_questions:
		current_questions.append([question,Vote.objects.filter(question=question).count()])



	context = {'past_questions': past_questions, 
			'open_questions': open_questions, 
			'closed_questions': closed_questions,
			'current_questions': current_questions}
	return render(request, 'polls/index.html', context)

@login_required
@current_member_required
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
@current_member_required
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

	total_votes = Vote.objects.filter(question=question).count()
	context = {'question': question, 
				'question_open': question_open, 
				'choices': choices,
				'votes': votes,
				'total_votes': total_votes,
				}
	return render(request, 'polls/detail.html', context)


@login_required
@current_member_required
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

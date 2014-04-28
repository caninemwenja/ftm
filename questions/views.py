from __future__ import division

from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from .models import Question, MarkingAnswer
from .forms import QuestionForm, MarkingAnswerForm, StudentAnswerForm, MarkingForm

from lib import utils


@login_required
def home(request):
    questions = Question.objects.all()

    return render(request, "index.html", {'questions': questions})


@login_required
def add_question(request):
    form = QuestionForm(request.POST or None)

    if form.is_valid():
        form.instance.owner = request.user
        form.save()
        return redirect(reverse('home'))

    return render(request, "add_question.html", {'form': form})


@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to change that question's marking scheme")

    form = QuestionForm(request.POST or None, instance=question)

    if form.is_valid():
        form.save()
        return redirect(reverse('home'))

    return render(request, "edit_question.html", {'form': form})


@login_required
def view_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    return render(request, "question.html", {'question': question})


@login_required
def remove_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to change that question's marking scheme")

    question.delete()

    return redirect(reverse('home'))


@login_required
def publish_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.owner == request.user:
        question.published = True
        question.save()
        return redirect(reverse('home'))

    return HttpResponseForbidden("You're not allowed to publish that question")


@login_required
def marking_scheme(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to change that question's marking scheme")

    marking_answers = question.markinganswer_set.all()
    return render(request, "scheme.html", {'answers': marking_answers, 'question': question})


@login_required
def add_marking_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to change that question's marking scheme")

    form = MarkingAnswerForm(request.POST or None)

    if form.is_valid():
        form.instance.question = question
        form.save()

        return redirect(reverse("questions.scheme", args=(question.id,)))

    return render(request, "add_scheme.html", {'question': question, 'form': form})


@login_required
def edit_marking_answer(request, answer_id):
    answer = get_object_or_404(MarkingAnswer, pk=answer_id)

    if answer.question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to change that question's marking scheme")

    form = MarkingAnswerForm(request.POST or None, instance=answer)

    if form.is_valid():
        form.instance.question = answer.question
        form.save()

        return redirect(reverse("questions.scheme", args=(form.instance.question.id,)))

    return render(request, "edit_scheme.html", {'form': form})


@login_required
def remove_marking_answer(request, answer_id):
    answer = get_object_or_404(MarkingAnswer, pk=answer_id)

    if answer.question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to change that question's marking scheme")

    question = answer.question

    answer.delete()

    return redirect(reverse("questions.scheme", args=(question.id,)))


@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.published:
        return HttpResponseForbidden("The question is not yet published")

    form = StudentAnswerForm(request.POST or None)

    if form.is_valid():
        form.instance.question = question
        form.instance.student = request.user

        form.save()
        return redirect(reverse('home'))

    return render(request, "answer.html", {'form': form, 'question': question})


@login_required
def mark_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.owner != request.user:
        return HttpResponseForbidden("You're not allowed to mark that question")

    form = MarkingForm(request.POST or None)

    if form.is_valid():
        stemmer = form.cleaned_data['stemmer']
        wsd = form.cleaned_data['wsd']
        sim = form.cleaned_data['sim']
        scorer = form.cleaned_data['scorer']
        tentative_threshold_opt = form.cleaned_data['tentative_threshold']

        threshold_opt = form.cleaned_data['threshold'] if 'threshold' in form.cleaned_data else None

        results, threshold = question.mark(stemmer, wsd, sim, scorer, tentative_threshold_opt, threshold_opt)

        return render(request, 'results.html', {'results': results, 'question': question, 'threshold': threshold})

    return render(request, 'mark.html', {'form': form, 'question': question})


@login_required
def test_data(request):
    # one word
    question, created = Question.objects.get_or_create(owner=request.user, text="What is the capital of France?")

    question.markinganswer_set.get_or_create(text='Paris')

    question.published = True
    question.save()

    # multiple words
    question, created = Question.objects.get_or_create(owner=request.user, text="What is the function of Parliament?")

    question.markinganswer_set.get_or_create(text='Parliament is a law making institution')
    question.markinganswer_set.get_or_create(text='Parliament makes laws')
    question.markinganswer_set.get_or_create(text='Parliament is a government body')

    question.published = True
    question.save()

    return redirect(reverse('home'))
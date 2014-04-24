from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from .models import Question, MarkingAnswer
from .forms import QuestionForm, MarkingAnswerForm


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

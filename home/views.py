from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Problem , TestCase
from django.http import HttpResponseForbidden




def all_problems(request):
    problems = Problem.objects.all().order_by('id')
    return render(request, 'all_problems.html', {'problems': problems})


def problems_detail(request, id):
    problem = get_object_or_404(Problem, id=id)
    return render(request, 'problems_detail.html', {'problem': problem})

from django.shortcuts import render, redirect
from .forms import ProblemForm, TestCaseFormSet
from django.contrib.auth.decorators import login_required

@login_required
def create_problem(request):
    if request.method == 'POST':
        problem_form = ProblemForm(request.POST)
        test_case_formset = TestCaseFormSet(request.POST)

        if problem_form.is_valid() and test_case_formset.is_valid():
            problem = problem_form.save(commit=False)
            problem.creator = request.user  # Set the creator
            problem.save()

            for form in test_case_formset:
                if form.cleaned_data.get('input_data') and form.cleaned_data.get('output_data'):
                    test_case = form.save(commit=False)
                    test_case.problem = problem
                    test_case.save()

            return redirect('all_problems')
    else:
        problem_form = ProblemForm()
        test_case_formset = TestCaseFormSet()

    return render(request, 'create_problem.html', {
        'problem_form': problem_form,
        'test_case_formset': test_case_formset,
    })

@login_required
def edit_problem(request, id):
    problem = get_object_or_404(Problem, id=id)
    if problem.creator != request.user and not request.user.is_staff:
       return HttpResponseForbidden("You do not have permission to edit this problem.")

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, instance=problem)
        test_case_formset = TestCaseFormSet(request.POST, queryset=TestCase.objects.filter(problem=problem))

        if problem_form.is_valid() and test_case_formset.is_valid():
            problem_form.save()

            for form in test_case_formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:  # Make sure it's not a new, unsaved object
                        form.instance.delete()
                else:
                    test_case = form.save(commit=False)
                    test_case.problem = problem
                    test_case.save()

            return redirect('problems_detail', id=problem.id)
    else:
        problem_form = ProblemForm(instance=problem)
        test_case_formset = TestCaseFormSet(queryset=TestCase.objects.filter(problem=problem))

    return render(request, 'edit_problem.html', {
        'problem': problem,
        'problem_form': problem_form,
        'test_case_formset': test_case_formset,
    })


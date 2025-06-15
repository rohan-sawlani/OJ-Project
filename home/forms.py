from django import forms
from .models import Problem, TestCase
from django.forms import formset_factory

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'statement', 'input_format', 'output_format',
                  'constraints', 'sample_input', 'sample_output',
                  'difficulty', 'tags']

class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ['input_data', 'output_data']

from django.forms import modelformset_factory

TestCaseFormSet = modelformset_factory(
    TestCase,
    fields=('input_data', 'output_data'),
    extra=1,
    can_delete=True  
)

from django.db import models
from home.models import Problem
from django.contrib.auth.models import User
# Create your models here.

class CodeSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=100)
    code = models.TextField()
    input_data = models.TextField(null=True,blank=True)
    output_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=100, null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()

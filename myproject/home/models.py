from django.db import models

# Create your models here.
class poll(models.Model):
    statement = models.CharField(max_length=255)
    option1 = models.CharField(max_length=55)
    vote1 = models.IntegerField(default = 0)
    option2 = models.CharField(max_length=55)
    vote2 = models.IntegerField(default = 0)
    option3 = models.CharField(max_length=55)
    vote3 = models.IntegerField(default = 0)
    # problem1 = models.CharField(max_length=55)
    # problem2 = models.CharField(max_length=55)
    # problem3 = models.CharField(max_length=55)
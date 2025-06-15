from django.contrib import admin
from home.models import Problem, TestCase

class TestCaseInline(admin.TabularInline):  # or admin.StackedInline
    model = TestCase
    extra = 1  # Number of empty forms shown
    can_delete = True

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'creator', 'created_at')
    inlines = [TestCaseInline]  # This connects TestCases inline

admin.site.register(Problem, ProblemAdmin)

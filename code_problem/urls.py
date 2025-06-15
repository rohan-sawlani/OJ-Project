from django.urls import path
from . import views

app_name = 'code_problem'  # This is essential for namespacing

urlpatterns = [
    path('problem/<int:problem_id>/submit/', views.submit_code, name='submit'),
    path('history/<int:user_id>/', views.submission_history, name='submission_history'),
    path('view/<int:submission_id>/', views.view_code, name='view_code'),
]

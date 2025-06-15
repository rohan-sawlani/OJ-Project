from django.urls import path
from . import views

urlpatterns = [
    path('problems/', views.all_problems, name='all_problems'),
    path('problems/<int:id>/', views.problems_detail, name='problems_detail'),
    path('create/', views.create_problem, name='create_problem'),
    path('home/problem/<int:id>/edit/', views.edit_problem, name='edit_problem'),

]

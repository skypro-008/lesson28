from django.contrib import admin
from django.urls import path

from vacancies.views import VacancyListView, VacancyDetailView, VacancyCreateView, VacancyUpdateView, VacancyDeleteView

urlpatterns = [
    path('vacancy/', VacancyListView.as_view()),
    path('vacancy/create/', VacancyCreateView.as_view()),
    path('vacancy/<int:pk>/', VacancyDetailView.as_view()),
    path('vacancy/<int:pk>/update/', VacancyUpdateView.as_view()),
    path('vacancy/<int:pk>/delete/', VacancyDeleteView.as_view()),
]
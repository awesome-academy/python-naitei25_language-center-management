# quizzes/urls.py
from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    # Làm quiz của một bài học
    path("lesson/<int:lesson_id>/", views.quiz_detail, name="detail"),
]

from django.urls import path
from .views import mark_lesson_complete

app_name = 'user_progress'

urlpatterns = [
    path(
        'lessons/<int:lesson_id>/complete/',
        mark_lesson_complete,
        name='mark_lesson_complete'
    ),
]

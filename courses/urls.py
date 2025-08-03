from django.urls import path
from .views import (
    LessonListView, LessonCreateView,
    LessonUpdateView, LessonDeleteView, LessonDetailView
)

app_name = 'courses'

urlpatterns = [
    path('course/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson_list'),
    path('course/<int:course_id>/lessons/add/', LessonCreateView.as_view(), name='lesson_add'),
    path('lessons/<int:pk>/edit/', LessonUpdateView.as_view(), name='lesson_edit'),
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
]

# courses/urls.py
from django.urls import path
from .views import (
    CourseListView, MyCoursesView,
    LessonListView, LessonCreateView, LessonUpdateView, LessonDeleteView,
    CourseProgressView,
    LessonDetailView, LessonLearnView,
    CourseDetailView,
    QuizStartView, QuizTakeView, QuizResultView,
)

app_name = "courses"

urlpatterns = [
    # Danh sách khóa học
    path("", CourseListView.as_view(), name="list"),
    path("mine/", MyCoursesView.as_view(), name="my"),

    # CRUD bài học theo course_id (khu soạn nội dung)
    path("<int:course_id>/lessons/",        LessonListView.as_view(),  name="lesson_list"),
    path("<int:course_id>/lessons/new/",    LessonCreateView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/edit/",          LessonUpdateView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/",        LessonDeleteView.as_view(), name="lesson_delete"),

    # Tiến độ khóa học
    path("<int:course_id>/progress/",       CourseProgressView.as_view(), name="course_progress"),

    # Chi tiết khóa học theo ID (đặt trước route theo slug để tránh xung đột)
    path("by-id/<int:id>/", CourseDetailView.as_view(), name="detail_by_id"),
    path("<slug:slug>/",     CourseDetailView.as_view(), name="detail"),
    # Xem 1 bài đơn lẻ (template lesson_detail) — có slug cho đẹp URL
    path("<slug:slug>/lesson/<int:pk>/",    LessonDetailView.as_view(),   name="lesson_detail"),

    # Học bài với layout có playlist (learn)
    path("by-id/<int:course_id>/learn/<int:lesson_id>/", LessonLearnView.as_view(), name="lesson_by_id"),
    path("<slug:slug>/learn/<int:lesson_id>/", LessonLearnView.as_view(), name="lesson"),

    # QUIZ — by-id (PHẢI có 3 route này)
    path("by-id/<int:course_id>/quiz/<int:lesson_id>/start/",     QuizStartView.as_view(),  name="quiz_start_by_id"),
    path("by-id/<int:course_id>/quiz/take/<int:submission_id>/",  QuizTakeView.as_view(),   name="quiz_take_by_id"),
    path("by-id/<int:course_id>/quiz/result/<int:submission_id>/",QuizResultView.as_view(), name="quiz_result_by_id"),

    # QUIZ — theo slug (nếu sau này bạn có slug)
    path("<slug:slug>/quiz/<int:lesson_id>/start/",     QuizStartView.as_view(),  name="quiz_start"),
    path("<slug:slug>/quiz/take/<int:submission_id>/",  QuizTakeView.as_view(),   name="quiz_take"),
    path("<slug:slug>/quiz/result/<int:submission_id>/",QuizResultView.as_view(), name="quiz_result"),

    # Chi tiết khóa học theo slug (đặt cuối cùng)
    path("<slug:slug>/",                    CourseDetailView.as_view(),   name="detail"),
]

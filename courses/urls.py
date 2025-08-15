# courses/urls.py
from django.urls import path
from . import views
from .views import CourseCreateView, CourseUpdateView

app_name = "courses"

urlpatterns = [
    # Danh sách khóa học (lưới card + tìm kiếm/sort/paginate)
    path("", views.CourseListView.as_view(), name="list"),

    # Khóa học của tôi (lọc theo user)
    path("mine/", views.MyCoursesView.as_view(), name="my"),

    # Danh sách bài học (view quản trị/soạn bài theo course_id)
    path("<int:course_id>/lessons/", views.LessonListView.as_view(), name="lesson_list"),
    path("<int:course_id>/lessons/new/", views.LessonCreateView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/edit/", views.LessonUpdateView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/", views.LessonDeleteView.as_view(), name="lesson_delete"),

    # Tiến độ theo khóa (giữ tương thích view cũ)
    path("<int:course_id>/progress/", views.CourseProgressView.as_view(), name="course_progress"),

    # Học 1 bài (dựa vào pk bài; slug chỉ để đẹp URL)
    path("<slug:slug>/lesson/<int:pk>/", views.LessonDetailView.as_view(), name="lesson"),

    # Trang chi tiết khóa học
    # (đặt dưới các path tĩnh để tránh nuốt 'mine/')
    path("<slug:slug>/", views.CourseDetailView.as_view(), name="detail"),

    # Tùy chọn: tương thích theo id (nếu trước đây bạn dùng id)
    path("by-id/<int:course_id>/", views.CourseDetailView.as_view(), name="detail_by_id"),
    path("create/", CourseCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", CourseUpdateView.as_view(), name="edit"),
]

# custom_admin/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn cho trang dashboard chính của hệ thống quản trị tùy chỉnh
    # Đường dẫn này sẽ tương ứng với URL '/custom-admin/'
    path('', views.custom_admin_dashboard_view, name='dashboard'),
    
    # Các đường dẫn khác cho các trang quản lý
    # Ví dụ:
    path('users/', views.user_management_view, name='user_management'),
    path('courses/', views.course_management_view, name='course_management'),
    path('quizzes/', views.quiz_management_view, name='quiz_management'),
]

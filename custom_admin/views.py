# custom_admin/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def custom_admin_dashboard_view(request):
    return render(request, 'custom_admin/dashboard.html', {})

@user_passes_test(is_superuser)
def user_management_view(request):
    # Logic cho trang quản lý người dùng
    return render(request, 'custom_admin/user_management.html', {})

@user_passes_test(is_superuser)
def course_management_view(request):
    # Logic cho trang quản lý khóa học
    return render(request, 'custom_admin/course_management.html', {})

@user_passes_test(is_superuser)
def quiz_management_view(request):
    # Logic cho trang quản lý quiz
    return render(request, 'custom_admin/quiz_management.html', {})

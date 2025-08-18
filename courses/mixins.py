# courses/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import Course, Lesson
from .utils import user_can_access_course

class CourseAccessRequiredMixin(LoginRequiredMixin):
    login_url = "account_login"  # đổi theo project của bạn

    def dispatch(self, request, *args, **kwargs):
        course = None

        # 1) ưu tiên slug nếu URL có
        slug = kwargs.get("slug")
        if slug:
            try:
                # nếu Course có field slug thì lấy theo slug
                Course._meta.get_field("slug")
                course = get_object_or_404(Course, slug=slug)
            except Exception:
                course = None

        # 2) nếu chưa có, thử theo id trong URL
        if course is None:
            course_id = kwargs.get("course_id") or kwargs.get("id")
            if course_id:
                course = get_object_or_404(Course, pk=course_id)

        # 3) cuối cùng, suy ra từ lesson_id (nếu có)
        if course is None:
            lesson_id = kwargs.get("lesson_id")
            if lesson_id:
                lesson = get_object_or_404(Lesson, pk=lesson_id)
                course = lesson.course

        if course is None:
            return HttpResponseForbidden("Không xác định được khóa học.")

        self.course = course

        # Kiểm tra quyền truy cập
        if not user_can_access_course(request.user, course):
            return HttpResponseForbidden("Bạn cần được duyệt để xem nội dung khóa học.")

        return super().dispatch(request, *args, **kwargs)

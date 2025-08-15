# courses/views.py
from urllib.parse import urlparse, parse_qs
import re

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)

from core import constants as C
from .forms import LessonForm, CourseForm
from .models import Course, Lesson
from user_progress.models import LessonProgress


# ------------------------------
# Helpers
# ------------------------------
def _extract_youtube_id(url: str) -> str:
    """
    Trích xuất ID YouTube an toàn cho nhiều dạng URL.
    """
    if not url:
        return ""
    try:
        u = urlparse(url)
        host = (u.netloc or "").replace("www.", "")
        if host == "youtu.be":
            return u.path.lstrip("/")
        if "youtube.com" in host:
            # /shorts/<id>  |  /embed/<id>  |  /watch?v=<id>
            if u.path.startswith("/shorts/") or u.path.startswith("/embed/"):
                parts = u.path.split("/")
                return parts[2] if len(parts) > 2 else ""
            return parse_qs(u.query).get("v", [""])[0]
        # Fallback regex nếu domain lạ
        m = re.search(r"(?:v=|youtu\.be/)([^&?/]+)", url)
        return m.group(1) if m else ""
    except Exception:
        return ""


# ------------------------------
# Course listing (UI mới)
# ------------------------------
class CourseListView(LoginRequiredMixin, ListView):
    """
    Danh sách khóa học (hiển thị dạng lưới card).
    - Tìm kiếm theo q (name)
    - Sắp xếp theo popular/new/rating (có try/except để tránh field không tồn tại)
    - Paginate theo C.PAGINATION["COURSE_LIST_PAGE_SIZE"]
    """
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = C.PAGINATION["COURSE_LIST_PAGE_SIZE"]

    def get_queryset(self):
        qs = Course.objects.all().order_by("-id")
        q = self.request.GET.get("q")
        if q:
            # đổi 'name' -> 'title' nếu model của bạn dùng field khác
            qs = qs.filter(name__icontains=q)

        sort = self.request.GET.get("sort")
        try:
            if sort == "popular":
                qs = qs.order_by("-students_count", "-id")
            elif sort == "rating":
                qs = qs.order_by("-rating_avg", "-rating_count")
            elif sort == "new":
                qs = qs.order_by("-created_at")
        except Exception:
            # nếu field không có, im lặng dùng mặc định
            pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        ctx["sort"] = self.request.GET.get("sort", "")
        # ListView + paginate_by => có sẵn page_obj; template dùng components/_pagination.html
        return ctx


# ------------------------------
# Course detail (UI mới)
# ------------------------------
class CourseDetailView(LoginRequiredMixin, DetailView):
    """
    Trang chi tiết khóa học: giới thiệu, danh sách bài học, nút Đăng ký/Vào học.
    Tự động lấy course theo slug/ID (tùy URL hiện tại).
    """
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    # chấp nhận slug hoặc id/course_id để tương thích URL cũ
    def get_object(self, queryset=None):
        kwargs = self.kwargs
        if "slug" in kwargs:
            return get_object_or_404(Course, slug=kwargs["slug"])
        if "course_id" in kwargs:
            return get_object_or_404(Course, id=kwargs["course_id"])
        if "pk" in kwargs:
            return get_object_or_404(Course, pk=kwargs["pk"])
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = ctx["course"]

        # Lấy toàn bộ lesson của khóa học, ưu tiên order nếu có
        try:
            lessons = course.lessons.all().order_by("order", "id")
        except Exception:
            lessons = course.lessons.all().order_by("id")

        # Đã ghi danh hay chưa: tạm suy luận từ có tiến độ trong khóa
        user_is_enrolled = LessonProgress.objects.filter(
            user=self.request.user, lesson__course=course
        ).exists()

        ctx.update({
            "lessons": lessons,
            "user_is_enrolled": user_is_enrolled,
        })
        return ctx


# ------------------------------
# Lesson List / CRUD (giữ tương thích)
# ------------------------------
class LessonListView(LoginRequiredMixin, ListView):
    model = Lesson
    template_name = "courses/lesson_list.html"
    context_object_name = "lessons"

    def get_queryset(self):
        self.course = get_object_or_404(Course, id=self.kwargs["course_id"])
        return (
            Lesson.objects.filter(course=self.course)
            .select_related("course")
            .order_by("order", "id")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["course"] = self.course
        completed_ids = (
            LessonProgress.objects
            .filter(user=self.request.user, lesson__in=data["lessons"])
            .values_list("lesson_id", flat=True)
        )
        data["completed_lessons"] = set(completed_ids)
        return data


class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def get_initial(self):
        return {"course": get_object_or_404(Course, id=self.kwargs["course_id"])}

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, id=self.kwargs["course_id"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("courses:lesson_list", kwargs={"course_id": self.kwargs["course_id"]})


class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def get_success_url(self):
        return reverse_lazy("courses:lesson_list", kwargs={"course_id": self.object.course.id})


class LessonDeleteView(LoginRequiredMixin, DeleteView):
    model = Lesson

    def get_success_url(self):
        return reverse_lazy("courses:lesson_list", kwargs={"course_id": self.object.course.id})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        course_id = self.object.course.id
        self.object.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "course_id": course_id})
        return HttpResponseRedirect(self.get_success_url())


class LessonDetailView(LoginRequiredMixin, DetailView):
    """
    Trang học 1 bài: hiển thị video (URL/file), nút làm quiz nếu có.
    """
    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        lesson = data["lesson"]

        embed_url = ""
        if lesson.video_url:
            vid = _extract_youtube_id(lesson.video_url)
            if vid:
                embed_url = f"https://www.youtube.com/embed/{vid}"

        data["embed_url"] = embed_url
        data["has_quiz"] = hasattr(lesson, "quiz")
        return data


# ------------------------------
# Course progress (giữ tương thích view cũ)
# ------------------------------
class CourseProgressView(LoginRequiredMixin, TemplateView):
    template_name = "courses/course_progress.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, id=self.kwargs["course_id"])
        total = course.lessons.count()
        completed = LessonProgress.objects.filter(
            user=self.request.user, lesson__course=course
        ).count()
        percent = int((completed / total) * 100) if total else 0
        ctx.update({
            "course": course,
            "total_lessons": total,
            "completed_lessons": completed,
            "percent": percent,
        })
        return ctx


# # ------------------------------
# # Home (có thể đặt ở project/views.py, giữ tạm tại đây cho tương thích)
# # ------------------------------
# def home_view(request):
#     news_qs = []
#     try:
#         from news.models import News
#         news_qs = News.objects.order_by("-published_at")[: C.HOMEPAGE["NEWS_LIMIT"]]
#     except Exception:
#         pass
#     return render(request, "home.html", {"news_list": news_qs})

class MyCoursesView(LoginRequiredMixin, ListView):
    """
    Danh sách 'Khóa học của tôi'.
    Ở đây suy luận từ LessonProgress: khóa học nào bạn đã có tiến độ => đã tham gia.
    Nếu bạn có model Enrollment riêng, thay truy vấn trong get_queryset().
    """
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = C.PAGINATION["COURSE_LIST_PAGE_SIZE"]

    def get_queryset(self):
        # Nếu dùng Enrollment:
        # return Course.objects.filter(enrollments__user=self.request.user).distinct().order_by('-id')

        # Suy luận từ LessonProgress
        return (
            Course.objects
                  .filter(lessons__lessonprogress__user=self.request.user)
                  .distinct()
                  .order_by("-id")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # tái sử dụng form tìm kiếm/sort nếu cần
        ctx["query"] = self.request.GET.get("q", "")
        ctx["sort"] = self.request.GET.get("sort", "")
        return ctx

class CourseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "courses.add_course"
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"
    success_url = reverse_lazy("courses:list")  # đổi theo URL bạn đang dùng

class CourseUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "courses.change_course"
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"
    success_url = reverse_lazy("courses:list")
# courses/views.py
from urllib.parse import urlparse, parse_qs
import re

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)

# Nếu bạn vẫn dùng core.constants cho paginate, giữ lại:
from core import constants as C  # <- có thể bỏ nếu không còn dùng
# Hằng số dùng trong file này: đưa hết vào constants.py để clean
from constants import (
    COURSE_QUERY_PARAM,
    COURSE_SORT_PARAM,
    COURSE_SORT_POPULAR,
    COURSE_SORT_RATING,
    COURSE_SORT_NEW,
    COURSE_ORDER_BY_POPULAR,
    COURSE_ORDER_BY_RATING,
    COURSE_ORDER_BY_NEW,
    LESSON_ORDERING_FALLBACK,
    LESSON_ORDERING_WITH_SECTION,
    YOUTUBE_EMBED_BASE,
    # COURSE_LIST_PAGE_SIZE,  # nếu bạn bỏ C.PAGINATION, hãy mở dòng này
)

from .forms import LessonForm, CourseForm
from .models import Course, Lesson
from user_progress.models import LessonProgress
from .mixins import CourseAccessRequiredMixin
from .utils import _extract_youtube_id
# Dùng model quiz từ app 'quizzes'
from quizzes.models import Quiz, Question, Choice, Submission, Answer

# ------------------------------
# Course listing
# ------------------------------
class CourseListView(LoginRequiredMixin, ListView):
    """
    Danh sách khóa học (grid).
    - Tìm kiếm theo ?q=
    - sort=?popular|rating|new
    - paginate
    """
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    # Dùng paginate từ core.constants (giữ nguyên)
    paginate_by = C.PAGINATION["COURSE_LIST_PAGE_SIZE"]
    # Nếu muốn chuyển về constants.py của bạn, dùng dòng dưới và bỏ dòng trên:
    # paginate_by = COURSE_LIST_PAGE_SIZE

    def get_queryset(self):
        qs = Course.objects.all().order_by("-id")

        q = self.request.GET.get(COURSE_QUERY_PARAM)
        if q:
            qs = qs.filter(name__icontains=q)

        sort = self.request.GET.get(COURSE_SORT_PARAM)
        try:
            if sort == COURSE_SORT_POPULAR:
                qs = qs.order_by(*COURSE_ORDER_BY_POPULAR)
            elif sort == COURSE_SORT_RATING:
                qs = qs.order_by(*COURSE_ORDER_BY_RATING)
            elif sort == COURSE_SORT_NEW:
                qs = qs.order_by(*COURSE_ORDER_BY_NEW)
        except Exception:
            # nếu thiếu field, bỏ qua
            pass
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get(COURSE_QUERY_PARAM, "")
        ctx["sort"] = self.request.GET.get(COURSE_SORT_PARAM, "")
        return ctx


# ------------------------------
# Course detail
# ------------------------------
class CourseDetailView(DetailView):
    """
    Trang chi tiết khóa học.
    Hỗ trợ lấy theo slug (nếu model có) hoặc id ('pk' hoặc 'id' trong URL).
    """
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        qs = queryset or self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg)
        pk = self.kwargs.get(self.pk_url_kwarg) or self.kwargs.get("id")
        # Nếu model KHÔNG có field slug, khối slug dưới sẽ ném FieldError.
        # Ta bắt lỗi và rơi về pk.
        if slug:
            try:
                return get_object_or_404(qs, **{self.slug_field: slug})
            except Exception:
                pass
        if pk:
            return get_object_or_404(qs, pk=pk)
        raise AttributeError(
            f"{self.__class__.__name__} requires a slug ('{self.slug_url_kwarg}') "
            f"or a primary key ('{self.pk_url_kwarg}' or 'id') in the URL."
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = ctx["course"]
        # Lấy lesson theo order; nếu có section trong model thì ưu tiên sort theo section
        try:
            lessons = course.lessons.all().order_by(*LESSON_ORDERING_WITH_SECTION)
        except Exception:
            lessons = course.lessons.all().order_by(*LESSON_ORDERING_FALLBACK)
        # Suy luận "đã tham gia" từ LessonProgress (nếu bạn có Enrollment thì đổi tại đây)
        user_is_enrolled = LessonProgress.objects.filter(
            user=self.request.user, lesson__course=course
        ).exists()
        ctx.update({
            "lessons": lessons,
            "user_is_enrolled": user_is_enrolled,
        })
        return ctx


# ------------------------------
# Lesson List / CRUD
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
            .order_by(*LESSON_ORDERING_FALLBACK)
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
                embed_url = f"{YOUTUBE_EMBED_BASE}{vid}"

        data["embed_url"] = embed_url
        data["has_quiz"] = hasattr(lesson, "quiz")  # OneToOne related_name='quiz'
        return data


# ------------------------------
# Course progress
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


# ------------------------------
# Khóa học của tôi
# ------------------------------
class MyCoursesView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = C.PAGINATION["COURSE_LIST_PAGE_SIZE"]
    # hoặc: paginate_by = COURSE_LIST_PAGE_SIZE

    def get_queryset(self):
        # Nếu có Enrollment model, thay truy vấn theo Enrollment
        return (
            Course.objects
                  .filter(lessons__lessonprogress__user=self.request.user)
                  .distinct()
                  .order_by("-id")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get(COURSE_QUERY_PARAM, "")
        ctx["sort"] = self.request.GET.get(COURSE_SORT_PARAM, "")
        return ctx


# ------------------------------
# Học bài (layout có playlist + prev/next)
# ------------------------------
class LessonLearnView(CourseAccessRequiredMixin, DetailView):
    """
    Yêu cầu URL có 'slug' HOẶC 'course_id' để mixin xác thực.
    - Nếu có slug: filter theo course__slug.
    - Nếu không có slug: filter theo course_id truyền trong URL (fallback).
    """
    model = Lesson
    pk_url_kwarg = "lesson_id"
    template_name = "courses/lesson_learn.html"

    def get_queryset(self):
        qs = Lesson.objects.select_related("course")
        slug = self.kwargs.get("slug")

        if slug:
            try:
                Course._meta.get_field("slug")
                return qs.filter(course__slug=slug)
            except Exception:
                pass

        course_id = self.kwargs.get("course_id")
        if course_id:
            return qs.filter(course_id=course_id)

        lesson_id = self.kwargs.get("lesson_id")
        if lesson_id:
            try:
                course_id = Lesson.objects.only("course_id").get(pk=lesson_id).course_id
                return qs.filter(course_id=course_id)
            except Lesson.DoesNotExist:
                return qs.none()

        return qs.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lesson = self.object
        # playlist
        try:
            siblings = list(
                lesson.course.lessons.select_related("course").order_by(*LESSON_ORDERING_WITH_SECTION)
            )
        except Exception:
            siblings = list(
                lesson.course.lessons.select_related("course").order_by(*LESSON_ORDERING_FALLBACK)
            )
        ctx["siblings"] = siblings

        # prev/next
        idx = next((i for i, x in enumerate(siblings) if x.id == lesson.id), 0)
        ctx["prev_lesson"] = siblings[idx-1] if idx > 0 else None
        ctx["next_lesson"] = siblings[idx+1] if idx < len(siblings)-1 else None

        # URL nhúng YouTube
        embed_url = ""
        if getattr(lesson, "video_url", None):
            vid = _extract_youtube_id(lesson.video_url)
            if vid:
                embed_url = f"{YOUTUBE_EMBED_BASE}{vid}"
        ctx["embed_url"] = embed_url

        return ctx


# ------------------------------
# Quiz: start → take → result
# ------------------------------
class QuizStartView(CourseAccessRequiredMixin, View):
    template_name = "courses/quiz_start.html"

    def get(self, request, **kwargs):
        lesson_id = kwargs["lesson_id"]
        slug = kwargs.get("slug")
        if slug:
            try:
                lesson = get_object_or_404(Lesson, id=lesson_id, course__slug=slug)
            except Exception:
                lesson = get_object_or_404(Lesson, id=lesson_id)
        else:
            course_id = kwargs.get("course_id")
            if course_id:
                lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
            else:
                lesson = get_object_or_404(Lesson, id=lesson_id)

        quiz = get_object_or_404(Quiz, lesson=lesson)
        return render(
            request,
            self.template_name,
            {"lesson": lesson, "quiz": quiz, "course": getattr(self, "course", lesson.course)},
        )

    def post(self, request, **kwargs):
        lesson = get_object_or_404(Lesson, id=kwargs["lesson_id"])
        quiz = get_object_or_404(Quiz, lesson=lesson)
        sub = Submission.objects.create(quiz=quiz, user=request.user)  # started_at=now
        if "slug" in kwargs:
            return redirect("courses:quiz_take", slug=kwargs["slug"], submission_id=sub.id)
        course_id = kwargs.get("course_id")
        if course_id:
            return redirect("courses:quiz_take_by_id", course_id=course_id, submission_id=sub.id)
        return redirect("courses:quiz_take", slug=getattr(lesson.course, "slug", ""), submission_id=sub.id)


class QuizTakeView(CourseAccessRequiredMixin, View):
    template_name = "courses/quiz_take.html"

    def get(self, request, **kwargs):
        sub = get_object_or_404(
            Submission.objects.select_related("quiz__lesson__course"),
            id=kwargs["submission_id"],
            user=request.user,
        )
        quiz = sub.quiz
        end_at = sub.started_at + timezone.timedelta(minutes=quiz.time_minutes)
        questions = quiz.questions.prefetch_related("choices").order_by("order", "id")
        return render(
            request,
            self.template_name,
            {
                "submission": sub,
                "quiz": quiz,
                "questions": questions,
                "end_at": int(end_at.timestamp() * 1000),
            },
        )

    def post(self, request, **kwargs):
        sub = get_object_or_404(Submission, id=kwargs["submission_id"], user=request.user)
        quiz = sub.quiz
        # chấm điểm
        correct = wrong = skip = 0
        for q in quiz.questions.all():
            choice_id = request.POST.get(f"q{q.id}")  # value là choice.id
            if not choice_id:
                skip += 1
                Answer.objects.create(submission=sub, question=q, choice=None)
                continue
            ch = Choice.objects.filter(id=choice_id, question=q).first()
            Answer.objects.create(submission=sub, question=q, choice=ch)
            if ch and ch.is_correct:
                correct += 1
            else:
                wrong += 1
        sub.correct_cnt = correct
        sub.wrong_cnt = wrong
        sub.skip_cnt = skip
        sub.score = correct  # 1 câu = 1 điểm (tuỳ chỉnh nếu cần)
        sub.submitted_at = timezone.now()
        sub.save()

        if "slug" in kwargs:
            return redirect("courses:quiz_result", slug=kwargs["slug"], submission_id=sub.id)
        course_id = kwargs.get("course_id")
        if course_id:
            return redirect("courses:quiz_result_by_id", course_id=course_id, submission_id=sub.id)
        return redirect("courses:quiz_result", slug=getattr(sub.quiz.lesson.course, "slug", ""), submission_id=sub.id)


class QuizResultView(CourseAccessRequiredMixin, DetailView):
    model = Submission
    pk_url_kwarg = "submission_id"
    template_name = "courses/quiz_result.html"

    def get_queryset(self):
        return Submission.objects.select_related("quiz__lesson__course").filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sub = self.object
        # thời lượng làm bài (giây)
        duration_seconds = 0
        if sub.submitted_at and sub.started_at:
            duration_seconds = int((sub.submitted_at - sub.started_at).total_seconds())
        m, s = divmod(duration_seconds, 60)
        ctx["duration_seconds"] = duration_seconds
        ctx["duration_text"] = f"{m} phút {s} giây" if m else f"{s} giây"

        # (tuỳ chọn) đưa danh sách answer để render review
        ctx["answers"] = sub.answers.select_related("question", "choice").all()
        return ctx

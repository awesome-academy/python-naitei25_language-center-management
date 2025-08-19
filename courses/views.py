from __future__ import annotations

# ===== Stdlib =====
import re
from urllib.parse import urlparse, parse_qs

# ===== Django =====
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)

# ===== Project constants =====
from core import constants as C  # noqa: F401

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
    # COURSE_LIST_PAGE_SIZE,  # bật nếu bạn bỏ C.PAGINATION
    EnrollmentStatus,
)

# ===== Local apps =====
from .forms import LessonForm, CourseForm
from .mixins import CourseAccessRequiredMixin
from .models import Course, Lesson, Enrollment
from .utils import _extract_youtube_id

# Dùng models từ app quizzes (chỉ import cái nào bạn thật sự dùng)
from quizzes.models import Quiz, Question, Choice, Submission, Answer  # noqa: F401

from user_progress.models import LessonProgress  # noqa: F401
from django.urls import reverse
from .utils import _extract_youtube_id, user_can_access_course
from django.db.models import Q
from django.db.models import Prefetch

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
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    pk_url_kwarg = "pk"

    # KHÔNG prefetch lessons__section nếu không có field section
    def get_queryset(self):
        qs = super().get_queryset()
        # Nếu chắc Lesson có related_name='lessons' bạn có thể prefetch ở đây.
        # Để an toàn (tránh cấu hình khác), ta bỏ qua prefetch tại đây.
        return qs

    def get_object(self, queryset=None):
        qs = queryset or self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug:
            return get_object_or_404(qs, **{self.slug_field: slug})
        pk = self.kwargs.get(self.pk_url_kwarg) or self.kwargs.get("id") or self.kwargs.get("course_id")
        return get_object_or_404(qs, pk=pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.object

        # ---- Lessons (an toàn cho cả khi KHÔNG có section) ----
        lessons_qs = Lesson.objects.filter(course=course)
        if HAS_LESSON_SECTION:
            lessons_qs = lessons_qs.select_related("section")
            try:
                ordering = list(LESSON_ORDERING_WITH_SECTION)  # ví dụ: ("section__id", "order", "id")
            except NameError:
                ordering = ["section_id", "order", "id"]
        else:
            try:
                ordering = list(LESSON_ORDERING_FALLBACK)      # ví dụ: ("order", "id")
            except NameError:
                ordering = ["order", "id"]

        ctx["lessons"] = lessons_qs.order_by(*ordering)

        # ---- Enrollment / quyền truy cập ----
        user = self.request.user
        enrollment = None
        if user.is_authenticated:
            enrollment = (
                Enrollment.objects
                .filter(user=user, course=course)
                .only("id", "status", "approved_at")
                .first()
            )
        ctx["enrollment"] = enrollment
        ctx["user_is_enrolled"] = (
            bool(enrollment and enrollment.status == EnrollmentStatus.APPROVED.value)
            or (user.is_authenticated and (user.is_staff or user.is_superuser))
        )
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
    template_name = "courses/my_courses.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        user = self.request.user

        # Enrollments đã duyệt của user
        approved_enr_qs = (
            Enrollment.objects
            .filter(user=user, status=EnrollmentStatus.APPROVED.value)
            .only("id", "course_id", "approved_at", "status")
        )

        qs = (
            Course.objects
            .filter(enrollments__in=approved_enr_qs)
            .prefetch_related(
                Prefetch("enrollments", queryset=approved_enr_qs, to_attr="my_enrollments"),
                "lessons"  # nếu Lesson có related_name='lessons'; nếu không thì xoá dòng này
            )
            .distinct()
            .order_by("-enrollments__approved_at", "-id")
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = _("Khóa học của tôi")
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

from django.core.exceptions import FieldDoesNotExist

def _model_has_field(model, field_name: str) -> bool:
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False

HAS_LESSON_SECTION = _model_has_field(Lesson, "section")


@login_required
@require_POST
def enroll_request(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course,
        defaults={"status": EnrollmentStatus.PENDING.value}
    )
    # Nếu từng bị từ chối → cho đăng ký lại
    if not created and enrollment.status == EnrollmentStatus.REJECTED.value:
        enrollment.status = EnrollmentStatus.PENDING.value
        enrollment.approved_at = None
        enrollment.save(update_fields=["status", "approved_at"])

    if enrollment.status == EnrollmentStatus.APPROVED.value:
        messages.info(request, _("You are already approved for this course."))
    else:
        messages.success(request, _("Your enrollment request has been sent."))
    return redirect(course.get_absolute_url() if hasattr(course, "get_absolute_url") else "/")

@staff_member_required
@require_POST
def approve_enrollment(request, enrollment_id):
    e = get_object_or_404(Enrollment, pk=enrollment_id)
    e.status = EnrollmentStatus.APPROVED.value
    e.approved_at = timezone.now()
    e.save(update_fields=["status", "approved_at"])
    messages.success(request, _("Enrollment approved."))
    return redirect(e.course.get_absolute_url())

# ===== Start course (đi tới bài học đầu tiên) =====
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
def start_course_id(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Lấy bài học đầu tiên theo thứ tự (ưu tiên theo section rồi order)
    first_lesson = (
        Lesson.objects.filter(course=course)
        .select_related("section")
        .order_by("section__id", "order", "id")
        .first()
    )
    if not first_lesson:
        messages.info(request, _("Khóa học chưa có bài học."))
        return redirect("courses:detail_by_id", pk=course.pk)

    if not user_can_access_course(request.user, course):
        messages.warning(request, _("Bạn cần được duyệt để bắt đầu học."))
        return redirect("courses:detail_by_id", pk=course.pk)

    return redirect("courses:lesson_by_id", course_id=course.pk, lesson_id=first_lesson.pk)


@login_required
def start_course_id(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = Lesson.objects.filter(course=course)
    if HAS_LESSON_SECTION:
        lessons = lessons.select_related("section")
        order = ("section_id", "order", "id")
    else:
        order = ("order", "id")
    first_lesson = lessons.order_by(*order).first()
    if not first_lesson:
        messages.info(request, _("Khóa học chưa có bài học."))
        return redirect("courses:detail_by_id", pk=course.pk)
    if not user_can_access_course(request.user, course):
        messages.warning(request, _("Bạn cần được duyệt để bắt đầu học."))
        return redirect("courses:detail_by_id", pk=course.pk)
    return redirect("courses:lesson_by_id", course_id=course.pk, lesson_id=first_lesson.pk)

@login_required
def start_course_slug(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = Lesson.objects.filter(course=course)
    if HAS_LESSON_SECTION:
        lessons = lessons.select_related("section")
        order = ("section_id", "order", "id")
    else:
        order = ("order", "id")
    first_lesson = lessons.order_by(*order).first()
    if not first_lesson:
        messages.info(request, _("Khóa học chưa có bài học."))
        return redirect("courses:detail", slug=course.slug)
    if not user_can_access_course(request.user, course):
        messages.warning(request, _("Bạn cần được duyệt để bắt đầu học."))
        return redirect("courses:detail", slug=course.slug)
    return redirect("courses:lesson", slug=course.slug, lesson_id=first_lesson.pk)


# ===== Enroll (đăng ký học) theo ID & slug =====
@login_required
@require_POST
def enroll_request(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enr, created = Enrollment.objects.get_or_create(
        user=request.user, course=course,
        defaults={"status": EnrollmentStatus.PENDING.value},
    )
    if not created and enr.status == EnrollmentStatus.REJECTED.value:
        enr.status = EnrollmentStatus.PENDING.value
        enr.approved_at = None
        enr.save(update_fields=["status", "approved_at"])

    if enr.status == EnrollmentStatus.APPROVED.value:
        messages.info(request, _("Bạn đã được duyệt khóa học này."))
    else:
        messages.success(request, _("Yêu cầu đăng ký đã được gửi."))

    return redirect("courses:detail_by_id", pk=course.pk)


@login_required
@require_POST
def enroll_request_slug(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enr, created = Enrollment.objects.get_or_create(
        user=request.user, course=course,
        defaults={"status": EnrollmentStatus.PENDING.value},
    )
    if not created and enr.status == EnrollmentStatus.REJECTED.value:
        enr.status = EnrollmentStatus.PENDING.value
        enr.approved_at = None
        enr.save(update_fields=["status", "approved_at"])

    if enr.status == EnrollmentStatus.APPROVED.value:
        messages.info(request, _("Bạn đã được duyệt khóa học này."))
    else:
        messages.success(request, _("Yêu cầu đăng ký đã được gửi."))

    return redirect("courses:detail", slug=course.slug)
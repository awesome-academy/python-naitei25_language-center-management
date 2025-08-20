from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from constants import MAX_STATUS_LENGTH, STATUS_CHOICES, EnrollmentStatus

from constants import (
    # Course & Lesson
    COURSE_NAME_MAX_LENGTH,
    LESSON_TITLE_MAX_LENGTH,
    LESSON_ORDER_DEFAULT,
    COURSE_COVER_UPLOAD_PATH,
    LESSON_VIDEO_UPLOAD_PATH,
    COURSE_DEFAULT_ORDERING,
    LESSON_DEFAULT_ORDERING,
    LESSON_UNIQUE_TOGETHER,

    # Section
    SECTION_TITLE_MAX_LENGTH,
    SECTION_ORDER_DEFAULT,

    # Enrollment
    ENROLLMENT_STATUS_MAX_LENGTH,

    # Messages
    LESSON_VIDEO_REQUIRED_MSG,
)


class Course(models.Model):
    name = models.CharField(_("Course Name"), max_length=COURSE_NAME_MAX_LENGTH)
    description = models.TextField(_("Description"), blank=True)
    cover = models.ImageField(
        _("Cover Image"),
        upload_to=COURSE_COVER_UPLOAD_PATH,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = COURSE_DEFAULT_ORDERING

    def __str__(self) -> str:
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Course"),
    )
    title = models.CharField(_("Lesson Title"), max_length=LESSON_TITLE_MAX_LENGTH)
    description = models.TextField(_("Description"), blank=True)
    order = models.PositiveIntegerField(_("Order"), default=LESSON_ORDER_DEFAULT)

    video_url = models.URLField(_("Video URL"), blank=True, null=True)
    video_file = models.FileField(
        _("Video File"),
        upload_to=LESSON_VIDEO_UPLOAD_PATH,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = LESSON_DEFAULT_ORDERING
        unique_together = (LESSON_UNIQUE_TOGETHER,)

    def __str__(self) -> str:
        return f"{self.course.name} – {self.title}"

    def clean(self):
        # bắt buộc có 1 trong 2: video_url hoặc video_file
        if not self.video_url and not self.video_file:
            raise ValidationError({"video_url": _(LESSON_VIDEO_REQUIRED_MSG)})


class EnrollmentStatus(models.TextChoices):
    PENDING  = "PENDING",  _("Chờ duyệt")
    APPROVED = "APPROVED", _("Đã duyệt")
    REJECTED = "REJECTED", _("Từ chối")


class Enrollment(models.Model):
    user   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=ENROLLMENT_STATUS_MAX_LENGTH,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.PENDING,
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "course")


class Section(models.Model):
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="sections",
    )
    title  = models.CharField(max_length=SECTION_TITLE_MAX_LENGTH)
    order  = models.PositiveIntegerField(default=SECTION_ORDER_DEFAULT)

    def __str__(self) -> str:
        return f"{self.course.name} – {self.title}"


class LessonKind(models.TextChoices):
    VIDEO = "VIDEO", _("Video")
    NOTE  = "NOTE",  _("Ghi chú")
    QUIZ  = "QUIZ",  _("Bài kiểm tra")

class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name=_("User"),
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name=_("Course"),
    )
    status = models.CharField(
        _("Status"),
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default=EnrollmentStatus.PENDING.value,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    approved_at = models.DateTimeField(_("Approved at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} → {self.course} [{self.status}]"

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from constants import (
    COURSE_NAME_MAX_LENGTH,
    LESSON_TITLE_MAX_LENGTH,
    LESSON_ORDER_DEFAULT,
)



class Course(models.Model):
    name = models.CharField(_("Course Name"), max_length=COURSE_NAME_MAX_LENGTH)
    description = models.TextField(_("Description"), blank=True)
    cover = models.ImageField(
        _("Cover Image"),
        upload_to="courses/covers/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        "courses.Course",  # chỉ rõ app label để tránh mơ hồ
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
        upload_to="lessons/videos/",
        blank=True,
        null=True,
        help_text=_("Upload video file (mp4, webm, …) if you don't use a YouTube URL."),
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ["course", "order"]
        unique_together = (("course", "order"),)

    def __str__(self) -> str:
        return f"{self.course.name} – {self.title}"

    def clean(self):
        # Nếu cả hai đều trống thì báo lỗi nhẹ nhàng
        if not self.video_url and not self.video_file:
            raise ValidationError(
                {"video_url": _("Provide either a Video URL or upload a Video File.")}
            )

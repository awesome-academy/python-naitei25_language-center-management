from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from courses.models import Lesson

class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progresses',
        verbose_name=_("User")
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name=_("Lesson")
    )
    completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Completed At")
    )
    snapshot = models.JSONField(
        _("Lesson Snapshot"),
        help_text=_("Bản ghi lại nội dung Lesson tại thời điểm hoàn thành")
    )

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name = _("Lesson Progress")
        verbose_name_plural = _("Lesson Progresses")

    def __str__(self):
        return f"{self.user} – {self.lesson} @ {self.completed_at}"

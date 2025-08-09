from django.db import models
from django.utils.translation import gettext_lazy as _
from constants import (COURSE_NAME_MAX_LENGTH,LESSON_TITLE_MAX_LENGTH,LESSON_ORDER_DEFAULT,StatusEnum,STATUS_CHOICES,MAX_STATUS_LENGTH)

class Course(models.Model):
    name = models.CharField(_("Course Name"), max_length=COURSE_NAME_MAX_LENGTH)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ['name']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("Course")
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
        help_text=_("Upload video file (mp4, webm, …) nếu không dùng YouTube URL.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    class Meta:
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ['course', 'order']
        unique_together = (('course', 'order'),)

    def __str__(self):
        return f"{self.course.name} – {self.title}"
    
class UserCourse(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='registered_courses', verbose_name=_('User'))
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='registered_users', 
        verbose_name=_('Course')
    )

    status = models.CharField(
        max_length=MAX_STATUS_LENGTH,
        choices=STATUS_CHOICES,
        default=StatusEnum.PENDING.value,
        verbose_name=_('Status')
    )

    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Registered At'))

    class Meta:
        verbose_name = _('User Course')
        verbose_name_plural = _('User Courses')
        unique_together = (('user', 'course'),)

    def __str__(self):
        return f"{self.user.email} - {self.course.name} - {self.status}"

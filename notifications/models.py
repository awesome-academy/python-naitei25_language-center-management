from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from courses.models import Course

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Người dùng')
    )
    message = models.TextField(verbose_name=_('Nội dung thông báo'))
    is_read = models.BooleanField(default=False, verbose_name=_('Đã đọc'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Thời điểm tạo'))

    class Meta:
        verbose_name = _('Notifications')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.message[:30]}..."

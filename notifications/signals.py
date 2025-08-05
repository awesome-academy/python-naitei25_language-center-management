from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from courses.models import UserCourse
from .services import create_course_notification

# Biến toàn cục để lưu trạng thái cũ tạm thời (chỉ có tác dụng trong 1 lần save)
_old_status_cache = {}

@receiver(pre_save, sender=UserCourse)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _old_status_cache[instance.pk] = old_instance.status
        except sender.DoesNotExist:
            _old_status_cache[instance.pk] = None

@receiver(post_save, sender=UserCourse)
def user_course_status_changed(sender, instance, created, **kwargs):
    if created:
        return

    old_status = _old_status_cache.pop(instance.pk, None)

    if old_status != instance.status:
        create_course_notification(
            user=instance.user,
            course=instance.course,
            status=instance.status
        )

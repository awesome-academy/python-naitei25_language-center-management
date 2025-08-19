from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from django.utils.translation import gettext as _
from constants import StatusEnum


def create_course_notification(user, course, status):
    if status == StatusEnum.APPROVED.value:
        message = _("Bạn đã được duyệt tham gia khóa học '%(course_name)s'.") % {"course_name": course.name}
        subject = _("[Thông báo] Đăng ký khóa học '%(course_name)s' được duyệt") % {"course_name": course.name}
    elif status == StatusEnum.REJECTED.value:
        message = _("Đơn đăng ký tham gia khóa học '%(course_name)s' của bạn đã bị từ chối.") % {"course_name": course.name}
        subject = _("[Thông báo] Đăng ký khóa học '%(course_name)s' bị từ chối") % {"course_name": course.name}
    else:
        message = _("Yêu cầu đăng ký của bạn cho khóa học '%(course_name)s' đang chờ duyệt.") % {'course_name': course.name}
        subject = _("[Thông báo] Đã gửi yêu cầu tham gia khóa học '%(course_name)s'") % {'course_name': course.name}

    # Ghi Notification vào hệ thống
    Notification.objects.create(
        user=user,
        message=message
    )

    # Gửi email
    try:
        send_mail(
            subject=subject,
            message=f"Xin chào {user.get_name()},\n\n{message}\n\nTrân trọng.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    except Exception as e:
        print(f"Lỗi gửi email: {e}")

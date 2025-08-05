from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def create_course_notification(user, course, status):
    if status == 'approved':
        message = f"Bạn đã được duyệt tham gia khóa học '{course.name}'."
        subject = f"[Thông báo] Đăng ký khóa học '{course.name}' được duyệt"
    elif status == 'rejected':
        message = f"Rất tiếc, bạn đã bị từ chối tham gia khóa học '{course.name}'."
        subject = f"[Thông báo] Đăng ký khóa học '{course.name}' bị từ chối"
    else:
        message = f"Yêu cầu đăng ký của bạn cho khóa học '{course.name}' đang chờ duyệt."
        subject = f"[Thông báo] Đã gửi yêu cầu tham gia khóa học '{course.name}'"

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

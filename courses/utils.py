from .models import Enrollment, EnrollmentStatus

def user_can_access_course(user, course):
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return Enrollment.objects.filter(user=user, course=course, status=EnrollmentStatus.APPROVED).exists()

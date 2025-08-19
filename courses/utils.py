from .models import Enrollment, EnrollmentStatus
import re
from urllib.parse import urlparse, parse_qs
from constants import EnrollmentStatus

def user_can_access_course(user, course):
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    return Enrollment.objects.filter(user=user, course=course, status=EnrollmentStatus.APPROVED).exists()

def _extract_youtube_id(url: str) -> str:
    """
    Trích xuất ID YouTube an toàn cho nhiều dạng URL.
    """
    if not url:
        return ""
    try:
        u = urlparse(url)
        host = (u.netloc or "").replace("www.", "")
        if host == "youtu.be":
            return u.path.lstrip("/")
        if "youtube.com" in host:
            # /shorts/<id>  |  /embed/<id>  |  /watch?v=<id>
            if u.path.startswith("/shorts/") or u.path.startswith("/embed/"):
                parts = u.path.split("/")
                return parts[2] if len(parts) > 2 else ""
            return parse_qs(u.query).get("v", [""])[0]
        # Fallback regex nếu domain lạ
        m = re.search(r"(?:v=|youtu\.be/)([^&?/]+)", url)
        return m.group(1) if m else ""
    except Exception:
        return ""


def user_can_access_course(user, course) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return Enrollment.objects.filter(
        user=user,
        course=course,
        status=EnrollmentStatus.APPROVED.value
    ).exists()

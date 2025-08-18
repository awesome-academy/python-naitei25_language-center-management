# courses/templatetags/course_media.py
from django import template
from django.templatetags.static import static
from django.utils.translation import gettext as _

register = template.Library()

def _resolve_cover_url(course, placeholder="img/placeholders/course.jpg"):
    """
    Trả về URL ảnh cover theo thứ tự ưu tiên:
    1) course.cover (upload) -> .url
    2) course.cover_url: http(s) dùng trực tiếp, còn lại coi là static path
    3) placeholder tĩnh
    """
    # 1) File upload
    cover_file = getattr(course, "cover", None)
    if cover_file:
        try:
            return cover_file.url
        except Exception:
            pass  # phòng khi file mất

    # 2) cover_url
    cover_url = getattr(course, "cover_url", "") or ""
    if cover_url:
        if cover_url.startswith("http"):
            return cover_url
        return static(cover_url)

    # 3) Placeholder
    return static(placeholder)

@register.simple_tag
def course_cover_url(course, placeholder="img/placeholders/course.jpg"):
    """Dùng trong template: {% course_cover_url course as url %}"""
    return _resolve_cover_url(course, placeholder)

@register.inclusion_tag("courses/includes/_course_cover_img.html")
def course_cover_img(course, classes="card-img-top object-fit-cover", alt=None,
                     placeholder="img/placeholders/course.jpg", loading="lazy"):
    """
    Render thẻ <img> đầy đủ, tái sử dụng ở nhiều nơi.
    - classes: class cho <img>
    - alt: nếu None -> lấy course.title / course.name / _("Ảnh khóa học")
    """
    alt_text = alt or (getattr(course, "title", None) or getattr(course, "name", None) or _("Ảnh khóa học"))
    return {
        "src": _resolve_cover_url(course, placeholder),
        "classes": classes,
        "alt": alt_text,
        "loading": loading,
    }

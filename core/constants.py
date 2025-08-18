# core/constants.py
from django.utils.translation import gettext_lazy as _

SITE = {
    "NAME": "JKokoro",  # tên riêng, không dịch
    "TAGLINE": _("Học nhanh – Tiến bộ mỗi ngày"),
    "LOGO_PATH": "img/logo.svg",
    "BRAND_URL": "/",
}

NAV = [
    {"name": _("Trang chủ"),           "url_name": "home"},
    {"name": _("Danh sách khóa học"),  "url_name": "courses:list"},
    {"name": _("Khóa học của tôi"),    "url_name": "courses:my"},
    # Nếu chưa có route name tổng quan tiến độ, có thể dùng đường dẫn tuyệt đối:
    {"name": _("Tiến độ"),             "url": "/progress/"},  # hoặc "url_name": "user_progress:overview"
]

PAGINATION = {
    "COURSE_LIST_PAGE_SIZE": 12,
}

HOMEPAGE = {
    "NEWS_LIMIT": 4,
    "HERO_TITLE": _("HỌC NHANH – ĐÁP NHANH 10.000 CÂU"),
    "HERO_SUBTITLE": _("Kaiwa theo chủ đề, luyện phản xạ, học mọi lúc mọi nơi."),
    "HERO_CTA_TEXT": _("Xem khóa học"),
    "HERO_CTA_URL_NAME": "courses:list",
}

COURSE_CARD = {
    "SHOW_RATING": True,
    "SHOW_STUDENT_COUNT": True,
    "ENROLL_BUTTON_TEXT": _("Đăng ký"),
}

QUIZ = {
    "SHOW_REVIEW_AFTER_SUBMIT": True,
    "PASS_BADGE_TEXT": _("Bạn đã vượt qua bài kiểm tra!"),
    "FAIL_BADGE_TEXT": _("Bạn chưa đạt, hãy thử lại nhé!"),
}

FOOTER = {
    "COPYRIGHT": _("© 2025 JKokoro. All rights reserved."),
    "LINKS": [
        {"label": _("Giới thiệu"), "url": "#"},
        {"label": _("Điều khoản"), "url": "#"},
        {"label": _("Liên hệ"),    "url": "#"},
    ],
}

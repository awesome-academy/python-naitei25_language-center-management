# core/constants.py

SITE = {
    "NAME": "JKokoro",
    "TAGLINE": "Học nhanh – Tiến bộ mỗi ngày",
    "LOGO_PATH": "img/logo.svg",
    "BRAND_URL": "/",
}

# core/constants.py
NAV = [
    {"name": "Trang chủ",            "url_name": "home"},
    {"name": "Danh sách khóa học",   "url_name": "courses:list"},
    {"name": "Khóa học của tôi",     "url_name": "courses:my"},     # <— SỬA CHỖ NÀY
    # "Tiến độ": nếu bạn chưa có route name tổng quan, tạm dùng đường dẫn tuyệt đối:
    {"name": "Tiến độ",              "url": "/progress/"}           # hoặc "url_name": "user_progress:overview"
]

PAGINATION = {
    "COURSE_LIST_PAGE_SIZE": 12,
}

HOMEPAGE = {
    "NEWS_LIMIT": 4,
    "HERO_TITLE": "HỌC NHANH – ĐÁP NHANH 10.000 CÂU",
    "HERO_SUBTITLE": "Kaiwa theo chủ đề, luyện phản xạ, học mọi lúc mọi nơi.",
    "HERO_CTA_TEXT": "Xem khóa học",
    "HERO_CTA_URL_NAME": "courses:list",
}

COURSE_CARD = {
    "SHOW_RATING": True,
    "SHOW_STUDENT_COUNT": True,
    "ENROLL_BUTTON_TEXT": "Đăng ký",
}

QUIZ = {
    "SHOW_REVIEW_AFTER_SUBMIT": True,
    "PASS_BADGE_TEXT": "Bạn đã vượt qua bài kiểm tra!",
    "FAIL_BADGE_TEXT": "Bạn chưa đạt, hãy thử lại nhé!",
}

FOOTER = {
    "COPYRIGHT": "© 2025 JKokoro. All rights reserved.",
    "LINKS": [
        {"label": "Giới thiệu", "url": "#"},
        {"label": "Điều khoản", "url": "#"},
        {"label": "Liên hệ", "url": "#"},
    ],
}

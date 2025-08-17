from enum import Enum

# ====== Common Enums ======
class UserRole(Enum):
    GUEST = "g"
    USER = "u"
    WEBSITE_ADMIN = "wa"
    SYSTEM_ADMIN = "sa"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class Gender(Enum):
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class ProgressStatus(Enum):
    ONGOING = "o"
    COMPLETED = "c"
    SUSPEND = "s"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class ApprovalStatus(Enum):
    DRAFT = "d"
    PENDING = "p"
    APPROVED = "a"
    REJECTED = "r"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


# ====== Generic defaults ======
COUNT_DEFAULT = 0
PROGRESS_DEFAULT = 0.0

# ====== Max lengths ======
MAX_USERNAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255
MAX_COUNTRY_LENGTH = 100
MAX_IMAGE_URL_LENGTH = 255
MAX_TITLE_LENGTH = 255
MAX_TYPE_LENGTH = 255
MAX_GENDER_LENGTH = 1
MAX_STATUS_LENGTH = 1
MAX_ROLE_LENGTH = 2
MAX_TOKEN_LENGTH = 255

# ====== Other numeric limits ======
MAX_SESSION_REMEMBER = 1209600
MAX_RATE = 5
MAX_AVATAR_SIZE = 1024 * 1024 * 5  # 5 MB

# ====== Minimums ======
MIN_RATE = 0
MIN_PASSWORD_LENGTH = 8
MIN_TEXTAREA_ROWS = 3
MIN_SESSION_REMEMBER = 0

# ====== Session ======
SESSION_COOKIE_AGE_SECONDS = 86400  # 24 hours

# ====== Course & Lesson ======
COURSE_NAME_MAX_LENGTH   = 200
LESSON_TITLE_MAX_LENGTH  = 200
LESSON_ORDER_DEFAULT     = 0

# Upload paths
COURSE_COVER_UPLOAD_PATH = "courses/covers/"
LESSON_VIDEO_UPLOAD_PATH = "lessons/videos/"

# Model meta (ordering, constraints…)
COURSE_DEFAULT_ORDERING = ["name"]
LESSON_DEFAULT_ORDERING = ["course", "order"]
LESSON_UNIQUE_TOGETHER  = ("course", "order")

# ====== Section ======
SECTION_TITLE_MAX_LENGTH = MAX_TITLE_LENGTH
SECTION_ORDER_DEFAULT    = 0

# ====== Enrollment ======
ENROLLMENT_STATUS_MAX_LENGTH = 16

# ====== Quiz & Question & Choice ======
QUIZ_TITLE_MAX_LENGTH    = 200
CHOICE_TEXT_MAX_LENGTH   = 255

# ====== Messages (plain string; i18n wrap at usage site) ======
LESSON_VIDEO_REQUIRED_MSG = "Provide either a Video URL or upload a Video File."

# Query params
COURSE_QUERY_PARAM = "q"
COURSE_SORT_PARAM  = "sort"

# Sort keys (giá trị trong ?sort=)
COURSE_SORT_POPULAR = "popular"
COURSE_SORT_RATING  = "rating"
COURSE_SORT_NEW     = "new"

# Trường sắp xếp tương ứng
COURSE_ORDER_BY_POPULAR = ("-students_count", "-id")
COURSE_ORDER_BY_RATING  = ("-rating_avg", "-rating_count")
COURSE_ORDER_BY_NEW     = ("-created_at",)

# Fallback ordering cho Lesson (khi không có Section)
LESSON_ORDERING_FALLBACK = ("order", "id")
# Ordering có Section (nếu field có tồn tại)
LESSON_ORDERING_WITH_SECTION = ("section__order", "order", "id")

# YouTube
YOUTUBE_EMBED_BASE = "https://www.youtube.com/embed/"

# Paginate (nếu bạn chưa có trong core.constants)
COURSE_LIST_PAGE_SIZE = 12  # có thể điều chỉnh
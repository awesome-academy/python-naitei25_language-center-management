import enum
from enum import Enum
from django.utils.translation import gettext_lazy as _

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


class StatusEnum(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

STATUS_CHOICES = [
    (StatusEnum.PENDING.value, _('Chờ duyệt')),
    (StatusEnum.APPROVED.value, _('Đã duyệt')),
    (StatusEnum.REJECTED.value, _('Từ chối')),
]


COUNT_DEFAULT = 0
PROGRESS_DEFAULT = 0.0

# Constants for max_length
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
MAX_STATUS_LENGTH = 20
MAX_ROLE_LENGTH = 2
MAX_SESSION_REMEMBER = 1209600
MAX_RATE = 5
MAX_TOKEN_LENGTH = 255

# Constants for min_length
MIN_RATE = 0
MIN_PASSWORD_LENGTH = 8
MIN_TEXTAREA_ROWS = 3
MIN_SESSION_REMEMBER = 0

# Session
SESSION_COOKIE_AGE_SECONDS = 86400  # 24 hours

# Course & Lesson 
COURSE_NAME_MAX_LENGTH   = 200
LESSON_TITLE_MAX_LENGTH  = 200
LESSON_ORDER_DEFAULT     = 0

# Quiz & Question & Choice
QUIZ_TITLE_MAX_LENGTH    = 200
CHOICE_TEXT_MAX_LENGTH   = 255
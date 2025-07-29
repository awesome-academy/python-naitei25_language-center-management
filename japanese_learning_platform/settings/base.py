"""
Cấu hình cơ bản cho dự án Django.
Các cài đặt chung cho cả môi trường phát triển và sản xuất.
"""

import os
from pathlib import Path
from decouple import config

# Định nghĩa đường dẫn gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Khóa bảo mật bí mật. NÊN THAY ĐỔI TRONG MÔI TRƯỜNG SẢN XUẤT!
# Lấy từ biến môi trường nếu có, nếu không thì dùng giá trị mặc định (chỉ cho phát triển)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-your-super-secret-key-for-development-only')

# Cài đặt DEBUG. NÊN ĐẶT LÀ False TRONG MÔI TRƯỜNG SẢN XUẤT!
DEBUG = True # Sẽ được ghi đè trong settings/production.py

# Các host được phép truy cập ứng dụng
ALLOWED_HOSTS = [] # Sẽ được cấu hình cụ thể hơn trong settings/development.py và settings/production.py

# Các ứng dụng Django đã cài đặt
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Các ứng dụng tùy chỉnh của bạn
    'core',
    'accounts',
    'courses',
    'quizzes',
    'user_progress',
    'notifications',
    'custom_admin', # Ứng dụng quản trị tùy chỉnh
]

# Middleware được sử dụng bởi Django
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Cấu hình URL gốc của dự án
ROOT_URLCONF = 'japanese_learning_platform.urls'

# Cấu hình các template
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Thư mục chứa các template chung của dự án
        'APP_DIRS': True, # Cho phép Django tìm template trong thư mục 'templates' của mỗi ứng dụng
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Cấu hình WSGI application
WSGI_APPLICATION = 'japanese_learning_platform.wsgi.application'

# Cấu hình cơ sở dữ liệu
# Mặc định sử dụng SQLite3 cho môi trường phát triển
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Cấu hình trình xác thực mật khẩu
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Cấu hình ngôn ngữ và múi giờ
LANGUAGE_CODE = 'vi-vn' # Ngôn ngữ tiếng Việt

TIME_ZONE = 'Asia/Ho_Chi_Minh' # Múi giờ Việt Nam

USE_I18N = True # Hỗ trợ quốc tế hóa

USE_TZ = True # Hỗ trợ múi giờ

# Cấu hình tệp tĩnh (CSS, JavaScript, hình ảnh)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static', # Thư mục chứa các tệp tĩnh chung của dự án
]
STATIC_ROOT = BASE_DIR / 'staticfiles' # Nơi Django thu thập các tệp tĩnh khi deploy

# Cấu hình tệp media (tệp người dùng tải lên)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media' # Nơi lưu trữ các tệp media

# Loại trường khóa chính mặc định cho các model
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cấu hình Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Cấu hình email (ví dụ cho phát triển, sẽ dùng console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

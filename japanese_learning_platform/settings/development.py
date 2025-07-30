# japanese_learning_platform/settings/development.py (or base.py)
"""
Cấu hình cho môi trường phát triển.
Kế thừa từ base.py và ghi đè các cài đặt cần thiết cho phát triển.
"""

from .base import *

# Bật chế độ DEBUG
DEBUG = True

# Cho phép tất cả các host khi ở chế độ DEBUG
ALLOWED_HOSTS += ['127.0.0.1', 'localhost']

# THÊM DÒNG NÀY ĐỂ KHAI BÁO ỨNG DỤNG CỦA BẠN
INSTALLED_APPS += [
    'accounts', # <-- THAY 'accounts' BẰNG TÊN ỨNG DỤNG THỰC TẾ CỦA BẠN
    # Đảm bảo app này được đặt sau 'django.contrib.auth' nếu bạn override User model
]
                                                                                                                                                                                                                                                                                                                                                
# Cấu hình email để hiển thị trong console (dễ debug)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Thêm Django Debug Toolbar nếu bạn muốn sử dụng (cần cài đặt thêm)
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]
# INTERNAL_IPS = [
#     '127.0.0.1',
# ]                                                                         

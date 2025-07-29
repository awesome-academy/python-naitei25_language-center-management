"""
WSGI config for japanese_learning_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'japanese_learning_platform.settings')
# Trong môi trường sản xuất, bạn sẽ cần cấu hình biến môi trường này để trỏ đến production.py
# Ví dụ: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'japanese_learning_platform.settings.production')

application = get_wsgi_application()

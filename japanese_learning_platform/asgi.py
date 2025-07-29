"""
ASGI config for japanese_learning_platform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'japanese_learning_platform.settings')
# Trong môi trường sản xuất, bạn sẽ cần cấu hình biến môi trường này để trỏ đến production.py
# Ví dụ: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'japanese_learning_platform.settings.production')

application = get_asgi_application()

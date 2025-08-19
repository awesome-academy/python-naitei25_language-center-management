from django.contrib import admin
from .models import Notification
from django.utils.html import format_html

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'short_message', 'is_read_icon', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'message')
    ordering = ('-created_at',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email người dùng"

    def short_message(self, obj):
        msg = obj.message or ""
        return msg if len(msg) <= 50 else msg[:50] + "..."  
    short_message.short_description = "Nội dung"

    def is_read_icon(self, obj):
        if obj.is_read:
            return format_html('<span style="color:green;">&#x2714;</span>')
        return format_html('<span style="color:red;">&#x2716;</span>')

    is_read_icon.short_description = "Trạng thái"
    is_read_icon.allow_tags = True   

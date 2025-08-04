from django.contrib import admin
from .models import Course, Lesson
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'video_preview')

    def video_preview(self, obj):
        if obj.video_url:
            # chỉ lấy iframe cho YouTube
            return format_html(
                '<iframe width="200" height="113" src="https://www.youtube.com/embed/{}" frameborder="0"></iframe>',
                obj.video_url.split('v=')[-1]
            )
        if obj.video_file:
            return format_html('<video width="200" controls src="{}"></video>', obj.video_file.url)
        return "-"
    video_preview.short_description = _("Preview")

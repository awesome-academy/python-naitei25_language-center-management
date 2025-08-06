from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from courses.models import Lesson
from .models import LessonProgress
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    snapshot = {
        'title':       lesson.title,
        'description': lesson.description,
        'order':       lesson.order,
        'video_url':   lesson.video_url,
        'video_file':  lesson.video_file.url if lesson.video_file else None,
        'course': {
            'id':   lesson.course.id,
            'name': lesson.course.name,
        }
    }
    obj, created = LessonProgress.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'snapshot': snapshot}
    )
    return JsonResponse({'success': True, 'created': created})

class CourseProgressView(LoginRequiredMixin, TemplateView):
    """
    Hiển thị tiến độ: số bài học đã hoàn thành / tổng số, kèm progress bar.
    """
    template_name = 'courses/course_progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Lấy course
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        # Tổng số bài học
        total = course.lesson_set.count()
        # Số bài đã hoàn thành của user
        completed = LessonProgress.objects.filter(
            user=self.request.user,
            lesson__course=course
        ).count()
        # Tỉ lệ % (integer)
        percent = int((completed / total) * 100) if total else 0

        context.update({
            'course': course,
            'total_lessons': total,
            'completed_lessons': completed,
            'percent': percent,
        })
        return context

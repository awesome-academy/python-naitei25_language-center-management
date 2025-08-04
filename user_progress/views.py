from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from courses.models import Lesson
from .models import LessonProgress

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

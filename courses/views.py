from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)
from .models import Course, Lesson
from .forms import LessonForm
from user_progress.models import LessonProgress
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
import re
from django.views.generic import TemplateView

class LessonListView(LoginRequiredMixin, ListView):
    model = Lesson
    template_name = 'courses/lesson_list.html'
    context_object_name = 'lessons'

    def get_queryset(self):
        self.course = get_object_or_404(Course, id=self.kwargs['course_id'])
        return Lesson.objects.filter(course=self.course)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['course'] = self.course
        completed = (
            LessonProgress.objects
            .filter(user=self.request.user, lesson__in=data['lessons'])
            .values_list('lesson_id', flat=True)
        )
        data['completed_lessons'] = set(completed)
        return data


class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def get_initial(self):
        # gán course nếu muốn ẩn field course trong form
        return {'course': get_object_or_404(Course, id=self.kwargs['course_id'])}

    def form_valid(self, form):
        form.instance.course = get_object_or_404(Course, id=self.kwargs['course_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:lesson_list', kwargs={'course_id': self.kwargs['course_id']})


class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def get_success_url(self):
        return reverse_lazy('courses:lesson_list', kwargs={'course_id': self.object.course.id})


class LessonDeleteView(LoginRequiredMixin, DeleteView):
    model = Lesson

    def get_success_url(self):
        return reverse_lazy('courses:lesson_list', kwargs={
            'course_id': self.object.course.id
        })

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        course_id = self.object.course.id
        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'course_id': course_id})
        return HttpResponseRedirect(self.get_success_url())

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        lesson = data['lesson']
        # Nếu có video_url, extract video_id để tạo embed_url
        embed_url = ''
        if lesson.video_url:
            m = re.search(r'(?:v=|youtu\.be/)([^&]+)', lesson.video_url)
            vid = m.group(1) if m else ''
            if vid:
                embed_url = f'https://www.youtube.com/embed/{vid}'
        data['embed_url'] = embed_url
        return data

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/course_progress.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        total = course.lessons.count()                   # related_name="lessons"
        completed = LessonProgress.objects.filter(
            user=self.request.user,
            lesson__course=course
        ).count()
        percent = int((completed / total) * 100) if total else 0

        ctx.update({
            'course': course,
            'total_lessons': total,
            'completed_lessons': completed,
            'percent': percent,
        })
        return ctx
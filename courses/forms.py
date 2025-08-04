from django import forms
from .models import Lesson

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'course', 'title', 'description', 'order',
            'video_url', 'video_file',
        ]

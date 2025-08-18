from django import forms
from .models import Lesson, Course

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'course', 'title', 'description', 'order',
            'video_url', 'video_file',
        ]

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "description", "cover"]  # thêm slug/level nếu bạn có
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }

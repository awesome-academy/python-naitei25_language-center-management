# quizzes/forms.py
from django import forms
from .models import Quiz, Question, Choice

class QuizForm(forms.Form):
    """
    Tạo các field động: mỗi Question là 1 ChoiceField (radio),
    choices lấy từ Choice model.
    """
    def __init__(self, *args, quiz: Quiz, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiz = quiz
        for question in quiz.questions.all().order_by('order'):
            field_name = f'question_{question.pk}'
            # Lấy các lựa chọn cho question
            choices = [(c.pk, c.text) for c in question.choices.all()]
            self.fields[field_name] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True,
            )

# quizzes/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Choice
from .forms import QuizForm

@login_required
def quiz_detail(request, lesson_id):
    """
    Hiển thị form quiz (GET) và xử lý kết quả (POST).
    """
    quiz = get_object_or_404(Quiz, lesson_id=lesson_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, quiz=quiz)
        if form.is_valid():
            total_q = quiz.questions.count()
            correct = 0
            # Tính số câu đúng
            for question in quiz.questions.all():
                sel_id = int(form.cleaned_data[f'question_{question.pk}'])
                choice = Choice.objects.get(pk=sel_id)
                if choice.is_correct:
                    correct += 1
            score = (correct / total_q) * 100
            passed = score >= quiz.pass_rate
            return render(request, 'quizzes/quiz_result.html', {
                'quiz': quiz,
                'score': round(score, 2),
                'passed': passed,
            })
    else:
        form = QuizForm(quiz=quiz)

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'form': form,
    })

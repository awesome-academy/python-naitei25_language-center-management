from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Choice
from .forms import QuizForm

@login_required
def quiz_detail(request, lesson_id):
    quiz = get_object_or_404(Quiz, lesson__id=lesson_id)
    course_id = quiz.lesson.course.id  # Lấy course_id để truyền về template

    if request.method == 'POST':
        form = QuizForm(request.POST, quiz=quiz)
        if form.is_valid():
            total_q = quiz.questions.count()
            correct = 0
            results = []

            for question in quiz.questions.all():
                try:
                    sel_id = int(form.cleaned_data[f'question_{question.pk}'])
                    selected = question.choices.get(pk=sel_id)
                    is_correct = selected.is_correct
                    if is_correct:
                        correct += 1
                except (KeyError, Choice.DoesNotExist, ValueError):
                    selected = None
                    is_correct = False

                results.append({
                    'question': question,
                    'selected': selected,
                    'is_correct': is_correct,
                    'correct_choice': question.choices.filter(is_correct=True).first(),
                })

            score = (correct / total_q) * 100
            passed = score >= quiz.pass_rate

            return render(request, 'quizzes/quiz_result.html', {
                'quiz': quiz,
                'score': round(score, 2),
                'passed': passed,
                'results': results,
                'course_id': course_id,  # Thêm dòng này
            })
    else:
        form = QuizForm(quiz=quiz)

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'form': form,
    })

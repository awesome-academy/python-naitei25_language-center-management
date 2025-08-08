from django import template
register = template.Library()

@register.simple_tag
def choice_style(choice, correct_choice, selected_choice):
    """
    Trả về style màu dựa trên đáp án đúng / đã chọn.
    """
    if choice == correct_choice:
        return 'color:green;'
    elif choice == selected_choice:
        return 'color:red;'
    return ''

@register.simple_tag
def choice_icon(choice, correct_choice, selected_choice, is_correct):
    """
    Trả về icon ✅ hoặc ❌ tuỳ thuộc vào kết quả.
    """
    if choice == correct_choice:
        return '✅'
    elif choice == selected_choice and not is_correct:
        return '❌'
    return ''

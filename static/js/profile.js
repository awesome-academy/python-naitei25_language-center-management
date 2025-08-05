document.addEventListener('DOMContentLoaded', function() {
    // Ẩn tất cả messages không nằm trong profile-box
    const allMessages = document.querySelectorAll('.messages, .django-messages, .alert, .message');
    const profileBox = document.querySelector('.profile-box');
    
    allMessages.forEach(function(msg) {
        if (!profileBox.contains(msg)) {
            msg.style.display = 'none';
            msg.style.visibility = 'hidden';
            msg.style.opacity = '0';
            msg.style.position = 'absolute';
            msg.style.left = '-9999px';
        }
    });
    
    // Ẩn các phần tử có text "Cập nhật thông tin thành công" không nằm trong profile-box
    const allElements = document.querySelectorAll('*');
    allElements.forEach(function(el) {
        if (el.textContent && el.textContent.trim() === 'Cập nhật thông tin thành công!' && !profileBox.contains(el)) {
            el.style.display = 'none';
        }
    });
});


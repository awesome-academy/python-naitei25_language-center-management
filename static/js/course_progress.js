// static/js/course_progress.js
(function() {
  document.addEventListener('DOMContentLoaded', function() {
    const bar = document.getElementById('course-progress-bar');
    if (!bar) return;
    // Lấy lại percent nếu muốn refresh
    const percent = bar.getAttribute('aria-valuenow');
    bar.style.width = percent + '%';
    bar.textContent = percent + '%';
  });
})();

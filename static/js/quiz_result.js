// static/js/quiz_result.js
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    const container = document.getElementById('quiz-result');
    if (!container || container.dataset.passed !== 'true') return;

    const url   = container.dataset.completeUrl;
    const csrftoken = container.dataset.csrfToken;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
    })
    .then(res => res.json())
    .then(data => console.log('Marked complete:', data))
    .catch(console.error);
  });
})();

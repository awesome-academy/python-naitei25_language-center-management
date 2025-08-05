(function(){
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(c => {
        const cookie = c.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.split('=')[1]);
        }
      });
    }
    return cookieValue;
  }

  const lessonId    = document.body.dataset.lessonId;
  const completeUrl = document.body.dataset.completeUrl;
  const statusBadge = document.getElementById('lesson-status');

  function markComplete() {
    fetch(completeUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        statusBadge.textContent = gettext('Completed');
        statusBadge.classList.remove('badge-secondary');
        statusBadge.classList.add('badge-success');
      }
    })
    .catch(console.error);
  }

  document.addEventListener('DOMContentLoaded', function(){
    // 1) HTML5 <video>
    const html5vid = document.querySelector('video');
    if (html5vid) {
      html5vid.addEventListener('ended', markComplete);
    }

    // 2) YouTube embed
    const iframe = document.querySelector('iframe');
    if (iframe && iframe.src.includes('youtube.com/embed')) {
      // Load YouTube Iframe API
      const tag = document.createElement('script');
      tag.src = "https://www.youtube.com/iframe_api";
      document.body.appendChild(tag);

      window.onYouTubeIframeAPIReady = function() {
        const player = new YT.Player(iframe, {
          events: {
            'onStateChange': ev => {
              if (ev.data === YT.PlayerState.ENDED) {
                markComplete();
              }
            }
          }
        });
      };
    }
  });
})();

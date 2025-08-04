(function(){
  function getCookie(name) {
    var cookieArr = document.cookie.split(';');
    for (var i = 0; i < cookieArr.length; i++) {
      var pair = cookieArr[i].trim().split('=');
      if (pair[0] === name) return decodeURIComponent(pair[1]);
    }
    return null;
  }
  var csrftoken = getCookie('csrftoken');
  var container = document.getElementById('lesson-detail');
  if (!container) return;
  var lessonId = container.dataset.lessonId;
  var videoEl = container.querySelector('video');
  if (videoEl) {
    videoEl.addEventListener('ended', function(){
      fetch('/progress/lessons/' + lessonId + '/complete/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
    });
  }
})();

(function(){
  // Lấy CSRF token từ cookie
  function getCookie(name) {
    var cookieArr = document.cookie.split(';');
    for (var i = 0; i < cookieArr.length; i++) {
      var pair = cookieArr[i].trim().split('=');
      if (pair[0] === name) return decodeURIComponent(pair[1]);
    }
    return null;
  }
  var csrftoken = getCookie('csrftoken');

  // Gán event delete cho các nút
  document.querySelectorAll('.js-delete-lesson').forEach(function(btn){
    btn.addEventListener('click', function(){
      if (!confirm('Bạn có chắc muốn xóa bài học này?')) return;
      var url = this.dataset.url;
      var rowId = this.dataset.id;
      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(function(r){ return r.json(); })
      .then(function(data){
        if (data.success) {
          var row = document.getElementById('lesson-row-' + rowId);
          if (row) row.remove();
        } else {
          alert('Xóa không thành công');
        }
      })
      .catch(function(){ alert('Lỗi kết nối'); });
    });
  });
})();

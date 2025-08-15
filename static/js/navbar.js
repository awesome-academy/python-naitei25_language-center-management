// Đổi style khi cuộn
(function(){
  const nav = document.querySelector('.navbar');
  if(!nav) return;
  window.addEventListener('scroll', () => {
    if(window.scrollY > 8){
      nav.classList.add('shadow');
    } else {
      nav.classList.remove('shadow');
    }
  });
})();

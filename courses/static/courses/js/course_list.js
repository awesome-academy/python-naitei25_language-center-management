// Ví dụ: cuộn lên đầu khi đổi trang
document.querySelectorAll('.pagination a').forEach(a=>{
  a.addEventListener('click', ()=> window.scrollTo({top:0, behavior:'smooth'}));
});

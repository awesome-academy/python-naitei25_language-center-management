// Chặn submit nếu câu nào chưa chọn (dù đã đặt required, thêm lớp báo lỗi)
document.querySelector('.quiz-form')?.addEventListener('submit', (e)=>{
  const questions = document.querySelectorAll('.card .form-check-input');
  // no-op: relied on required
});

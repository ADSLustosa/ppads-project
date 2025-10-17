
// simple auto carousel
let idx = 0;
function rotateSlides(){
  const slides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  slides.forEach((s,i)=>s.classList.toggle('active', i===idx));
  dots.forEach((d,i)=>d.classList.toggle('active', i===idx));
  idx = (idx+1)%slides.length;
}
setInterval(()=>{ if(document.querySelector('.carousel-container')) rotateSlides(); }, 5000);

// Basic example script to demonstrate dynamic behavior
document.addEventListener("DOMContentLoaded", function () {
  console.log("Blog page loaded");
  
  // Add smooth scrolling to all links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
  
  // Add fade-in animation to content
  const content = document.querySelector('.content');
  if (content) {
    content.style.opacity = '0';
    content.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      content.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      content.style.opacity = '1';
      content.style.transform = 'translateY(0)';
    }, 100);
  }
});

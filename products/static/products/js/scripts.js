document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById('enquiryForm');
  const icon = document.getElementById('enquiryIcon');
  const closeBtn = document.getElementById('closeEnquiry');
  const sendBtn = document.getElementById('sendEnquiryBtn');
  const sendBtn2 = document.getElementById('sendEnquiryBtn2');
  const sendBtn3 = document.getElementById('sendEnquiryBtn3');
  const sendBtn4 = document.getElementById('sendEnquiryBtn4');

  function showForm() {
    form.style.transform = 'translateX(0)';
    icon.style.display = 'none';
  }

  function hideForm() {
    form.style.transform = 'translateX(-120%)';
    icon.style.display = 'flex';
  }

  closeBtn.onclick = hideForm;
  icon.onclick = showForm;

  const sendButtons = [sendBtn, sendBtn2, sendBtn3, sendBtn4];
  sendButtons.forEach(btn => {
    if (btn) {
      btn.onclick = function (e) {
        e.preventDefault();
        showForm();
        form.scrollIntoView({ behavior: 'smooth' });
      };
    }
  });

  icon.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      icon.click();
    }
  });

  // Automatically hide form on small screens initially
  if (window.innerWidth <= 768) {
    hideForm();
  }
});

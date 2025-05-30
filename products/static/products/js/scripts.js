
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('enquiryForm');
    const icon = document.getElementById('enquiryIcon');
    const closeBtn = document.getElementById('closeEnquiry');
    const sendBtn = document.getElementById('sendEnquiryBtn'); // 👈 New

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

    if (sendBtn) {
      sendBtn.onclick = function (e) {
        e.preventDefault(); // Prevent default button behavior (optional)
        showForm();         // Show the floating form
        form.scrollIntoView({ behavior: 'smooth' }); // Optional: Scroll to form
      };
    }

    icon.addEventListener('keydown', function(event) {
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


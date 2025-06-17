
// document.addEventListener("DOMContentLoaded", function () {
//   const form = document.getElementById('enquiryForm');
//   const icon = document.getElementById('enquiryIcon');
//   const closeBtn = document.getElementById('closeEnquiry');

//   const sendButtons = [
//     document.getElementById('sendEnquiryBtn'),
//     document.getElementById('sendEnquiryBtn2'),
//     document.getElementById('sendEnquiryBtn3'),
//     document.getElementById('sendEnquiryBtn4')
//   ];

//   function showForm() {
//     form.style.transform = 'translateX(0)';
//     form.style.display = 'block'; // ensure visible
//     icon.style.display = 'none';
//   }

//   function hideForm() {
//     form.style.transform = 'translateX(-120%)';
//     setTimeout(() => {
//       form.style.display = 'none'; // hide it after animation
//     }, 300); // match transition duration if any
//     icon.style.display = 'flex';
//   }

//   if (closeBtn) {
//     closeBtn.addEventListener('click', hideForm);
//   }

//   if (icon) {
//     icon.addEventListener('click', showForm);

//     icon.addEventListener('keydown', function (event) {
//       if (event.key === 'Enter' || event.key === ' ') {
//         event.preventDefault();
//         showForm();
//       }
//     });
//   }

//   sendButtons.forEach(btn => {
//     if (btn) {
//       btn.addEventListener('click', function (e) {
//         e.preventDefault();
//         showForm();
//         form.scrollIntoView({ behavior: 'smooth' });
//       });
//     }
//   });

//   // Initial state for small screens
//   if (window.innerWidth <= 768) {
//     hideForm();
//   }
// });

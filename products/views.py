from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from .models import ContactSubmission
import mimetypes
from django.template.loader import render_to_string
from .models import Tally_1, Emudhra_2, Fusiontec_3, Biz_4
from django.contrib.auth import logout



def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, phone, subject, message]):
            messages.error(request, 'Please fill out all required fields.')
            return redirect('index')  # Replace with your actual URL name

        # Save to database
        ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )

        # Admin notification email
        email_html_content = render_to_string('products/contact_form_email.html', {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
        })

        # User thank-you email
        user_thank_you_content = render_to_string('products/contact_form_thanks.html', {
            'name': name,
        })

        try:
            # Send to admin
            email_msg = EmailMessage(
                subject=f"[Fusiontec Contact] - {subject}",
                body=email_html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_FORM_RECIPIENT],
            )
            email_msg.content_subtype = "html"
            email_msg.send()

            # Send thank you to user
            user_email = EmailMessage(
                subject="Thanks for contacting Fusiontec!",
                body=user_thank_you_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            user_email.content_subtype = "html"
            user_email.send()

            messages.success(request, 'Your message has been sent successfully.')
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')

    # for product section
    products = Tally_1.objects.all()    # First product model
    emudhra_products = Emudhra_2.objects.all()  # Second product model
    fusiontec_products = Fusiontec_3.objects.all()  #third product model
    biz_products = Biz_4.objects.all()  # Fourth product model

    context = {
        "products": products,
        "emudhra_products": emudhra_products,
        "fusiontec_products": fusiontec_products,
        "biz_products": biz_products,
    }

    # return render(request, "products.html", context)
    return render(request, 'products/index.html', context)


def custom_admin_logout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect('/')

def tally_form(request):
    return render(request, 'products/tally_form.html')

def emudhra_form(request):
    return render(request, 'products/emudhra_form.html')

def fusiontec_form(request):
    return render(request, 'products/fusiontec_form.html')

def biz_form(request):
    return render(request, 'products/biz_form.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from .models import ContactSubmission
from django.template.loader import render_to_string
from .models import Tally_1, Emudhra_2, Fusiontec_3, Biz_4
from .models import RazorpayInfo, CompanyPaymentInfoQR, BankTransferInfo
from .models import Emudhra_product
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EmudhraPriceListSubmission, biz_product

#for redirecting admin page to home page after logout
def custom_admin_logout(request):
    logout(request)
    messages.success(request, "Logout successfully")
    return redirect('/')

#------------------------------------------------------------------------------------------------
#home page view
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
    razorpay_infos = RazorpayInfo.objects.all() # for razorpay button
    payment_infos = CompanyPaymentInfoQR.objects.all()  #for QR section in Net banking
    bank_infos = BankTransferInfo.objects.all()   #for banking info in Net banking

    context = {
        "products": products,
        "emudhra_products": emudhra_products,
        "fusiontec_products": fusiontec_products,
        "biz_products": biz_products,
        'razorpay_infos': razorpay_infos,
        'payment_infos': payment_infos,
        'bank_infos': bank_infos
    }

    # return render(request, "products.html", context)
    return render(request, 'products/index.html', context)

#------------------------------------------------------------------------------------------------
import json
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .models import (TallyPriceListSubmission,Tally_1,Tally_Product,Tally_Software_Service,Tally_Upgrade)

logger = logging.getLogger(__name__)

def tally_form(request):
    # Render the HTML form template
    return render(request, 'products/tally_form.html')

@require_GET
def fetch_tally_details(request):
    product_type = request.GET.get('product_type')

    try:
        tally = Tally_1.objects.get(tally_name="Tally")
    except Tally_1.DoesNotExist:
        return JsonResponse({'error': 'Tally not found'}, status=404)

    if product_type == "product":
        items = Tally_Product.objects.filter(tally_1=tally)
    elif product_type == "service":
        items = Tally_Software_Service.objects.filter(tally_1=tally)
    elif product_type == "upgrade":
        items = Tally_Upgrade.objects.filter(tally_1=tally)
    else:
        return JsonResponse({'error': 'Invalid product_type'}, status=400)

    data = [{
        'type_name': item.type_name,
        'basic_amount': str(item.basic_amount),
        'cgst': str(item.cgst),
        'sgst': str(item.sgst),
        'total_price': str(item.total_price),
    } for item in items]

    return JsonResponse({'items': data}, status=200)

@csrf_exempt  # REMOVE this in production and use CSRF tokens instead!
def save_tally_form(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        logger.info(f"Received data for save_tally_form: {data}")

        pi = TallyPriceListSubmission.objects.create(
            customer_name=data.get('customer_name'),
            company_name=data.get('company_name'),
            has_gst=(data.get('has_gst') == 'yes'),
            gst_number=data.get('gst_number'),
            address=data.get('address'),
            state=data.get('state'),
            district=data.get('district'),
            pincode=data.get('pincode'),
            mobile=data.get('mobile'),
            email=data.get('email'),
            product_name=data.get('product_name'),
            product_type=data.get('product_type'),
            product_type_detail=data.get('product_type_detail'),
            basic_amount=data.get('basic_amount'),
            cgst=data.get('cgst'),
            sgst=data.get('sgst'),
            total_price=data.get('total_price'),
        )

        return JsonResponse({"success": True, "pi_id": pi.id})

    except Exception as e:
        logger.error(f"Error saving tally form: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=400)

#------------------------------------------------------------------------------------------------
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import EmudhraPriceListSubmission, Emudhra_product, Emudhra_2

# emudhra form view
def emudhra_form(request):
    emudhra_products = Emudhra_product.objects.all()
    emudhra_info = Emudhra_2.objects.first()

    return render(request, 'products/emudhra_form.html', {
        'emudhra_products': emudhra_products,
        'emudhra_info': emudhra_info,
    })

# for saving form for e-mudhra section
@csrf_exempt
def save_price_list_submission(request):
    if request.method == 'POST':
        data = request.POST

        # Safely convert numeric fields
        def to_decimal(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        submission = EmudhraPriceListSubmission.objects.create(
            customer_name = data.get('customer_name'),
            company_name = data.get('company_name'),
            has_gst = data.get('has_gst'),
            gst_number = data.get('gst_number'),
            address = data.get('address'),
            state = data.get('state'),
            district = data.get('district'),
            pincode = data.get('pincode'),
            mobile = data.get('mobile'),
            email = data.get('email'),
            product_name = data.get('product_name'),
            product_type_detail = data.get('product_type_detail'),
            basic_amount = to_decimal(data.get('basic_amount')),
            cgst = to_decimal(data.get('cgst')),
            sgst = to_decimal(data.get('sgst')),
            total_price = to_decimal(data.get('total_price')),
        )
        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
 

#------------------------------------------------------------------------------------------------
#fusiontec form view

def fusiontec_form(request):
    fusiontec_instance = get_object_or_404(Fusiontec_3, fusiontec_name="Fusiontec")  # or use pk if preferred
    products = fusiontec_instance.fusiontec_product_set.all()  # related products

    context = {
        'fusiontec_name': fusiontec_instance.fusiontec_name,
        'product_types': products,
    }
    return render(request, 'products/fusiontec_form.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FusiontecPriceListSubmission

@csrf_exempt
def fusiontec_price_list_form(request):
    if request.method == "POST":
        data = request.POST
        # Save data to model
        submission = FusiontecPriceListSubmission.objects.create(
            customer_name=data.get('customer_name'),
            company_name=data.get('company_name'),
            has_gst=data.get('has_gst'),
            gst_number=data.get('gst_number'),
            address=data.get('address'),
            state=data.get('state'),
            district=data.get('district'),
            pincode=data.get('pincode'),
            mobile=data.get('mobile'),
            email=data.get('email'),
            product_name=data.get('product_name'),
            product_type_detail=data.get('product_type_detail'),
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

#------------------------------------------------------------------------------------------------
#biz form view
from decimal import Decimal

def biz_form(request):
    bizz_products = biz_product.objects.all()
    bizz_info = Biz_4.objects.first()

    for plan in bizz_products:
        basic = plan.new_price or Decimal('0')
        plan.cgst = plan.cgst or round(basic * Decimal('0.09'), 2)
        plan.sgst = plan.sgst or round(basic * Decimal('0.09'), 2)
        plan.total_price = plan.total_price or round(basic + plan.cgst + plan.sgst, 2)

    return render(request, 'products/biz_form.html', {
        'bizz_products': bizz_products,
        'bizz_info': bizz_info,
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import BizPriceListSubmission

def save_pi_data(request):
    if request.method == 'POST':
        data = request.POST

        customer_name = data.get('customer_name', '')
        company_name = data.get('company_name', '')
        has_gst = data.get('has_gst', 'no')
        gst_number = data.get('gst_number', '')
        address = data.get('address', '')
        state = data.get('state', '')
        district = data.get('district', '')
        pincode = data.get('pincode', '')
        mobile = data.get('mobile', '')
        email = data.get('email', '')
        product_name = data.get('product_name', '')
        business_plan_id = data.get('business_plan')
        business_plan_name = ''
        original_price = 0
        new_price = 0
        cgst = 0
        sgst = 0
        total_price = 0

        try:
            # 🔧 Fetch from biz_product not BizPriceListSubmission
            plan = biz_product.objects.get(id=business_plan_id)
            business_plan_name = f"{plan.team_name}, {plan.billing_cycle}"
            original_price = plan.old_price or 0
            new_price = plan.new_price or 0
            cgst = plan.cgst or 0
            sgst = plan.sgst or 0
            total_price = plan.total_price or 0
        except biz_product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid business plan ID'}, status=400)

        pi = BizPriceListSubmission.objects.create(
            customer_name=customer_name,
            company_name=company_name,
            has_gst=has_gst,
            gst_number=gst_number,
            address=address,
            state=state,
            district=district,
            pincode=pincode,
            mobile=mobile,
            email=email,
            product_name=product_name,
            business_plan_id=int(business_plan_id),
            business_plan_name=business_plan_name,
            original_price=original_price,
            new_price=new_price,
            cgst=cgst,
            sgst=sgst,
            total_price=total_price,
        )
        return JsonResponse({'status': 'success', 'pi_id': pi.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
  
#--------------------------------------------------------------------------------------
# API for the dropdown form for State and district
import json, os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Load JSON on startup using absolute path
json_file_path = os.path.join(settings.BASE_DIR, 'data', 'states_districts.json')

try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        INDIA_DATA = json.load(f)["states"]
except FileNotFoundError:
    INDIA_DATA = []  # Fallback to empty list to prevent crash
    print(f"[ERROR] JSON file not found at: {json_file_path}")

@csrf_exempt
def get_states(request):
    state_names = sorted(state["state"] for state in INDIA_DATA if "state" in state)
    return JsonResponse({"states": state_names})

@csrf_exempt
def get_districts(request, state):
    # Case-insensitive state match
    matched = next((s for s in INDIA_DATA if s["state"].lower() == state.lower()), None)
    if matched and "districts" in matched:
        districts = sorted(matched["districts"])
    else:
        districts = []

    return JsonResponse({"districts": districts})

#---------------------------------------------------------------------------------------------
# razor pay integration in forms

import json
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import RazorpayTransactionForm

@csrf_exempt
def razorpay_verify(request):
    if request.method == "POST":
        data = json.loads(request.body)
        form_data = data.get("form_data", {})
        payment_id = data.get("razorpay_payment_id")
        order_id = data.get("razorpay_order_id")
        signature = data.get("razorpay_signature")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # 🔐 Step 1: Verify Razorpay Signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # ✅ Step 2: Fetch Payment Info
            payment = client.payment.fetch(payment_id)
            payment_status = payment.get("status")  # captured, failed, etc.

            if payment_status == "captured":
                final_status = "paid"
                amount = payment.get("amount") / 100  # Convert paisa to INR
            else:
                final_status = "failed"
                amount = 0

        except razorpay.errors.SignatureVerificationError:
            # ❌ Invalid signature (fraud attempt or error)
            final_status = "failed"
            amount = 0
        except Exception:
            # ❌ General failure (API error, etc.)
            final_status = "failed"
            amount = 0

        # 💾 Step 3: Save transaction to DB
        RazorpayTransactionForm.objects.create(
            customer_name=form_data.get("customer_name"),
            product_name=form_data.get("product_name"),
            amount=amount,
            razorpay_payment_id=payment_id,
            razorpay_order_id=order_id,
            status=final_status
        )

        return JsonResponse({"status": final_status})

@csrf_exempt
def create_order(request):
    if request.method == "POST":
        amount = int(float(request.POST.get("amount", "0"))) * 100  # in paisa
        customer_name = request.POST.get("customer_name")
        product_name = request.POST.get("product_name")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        RazorpayTransactionForm.objects.create(
            customer_name=customer_name,
            product_name=product_name,
            amount=amount / 100,
            razorpay_order_id=order["id"],
            status="created"
        )

        return JsonResponse({
            "order_id": order["id"],
            "key": settings.RAZORPAY_KEY_ID
        })
    
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .models import Applicant

@csrf_exempt
def dsctypeform(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pan_number = request.POST.get('pan_number')
        aadhar_number = request.POST.get('aadhar_number')
        mobile_number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        reference = request.POST.get('reference')
        reference_contact = request.POST.get('reference_contact')

        pan_copy = request.FILES.get('pan_copy')
        aadhar_copy = request.FILES.get('aadhar_copy')
        photo = request.FILES.get('photo')
        gst_certificate = request.FILES.get('gst_certificate')
        authorization_letter = request.FILES.get('authorization_letter')
        company_pan = request.FILES.get('company_pan')

        # Save applicant to DB
        Applicant.objects.create(
            name=name,
            pan_number=pan_number,
            aadhar_number=aadhar_number,
            mobile_number=mobile_number,
            email=email,
            reference=reference,
            reference_contact=reference_contact,
            pan_copy=pan_copy,
            aadhar_copy=aadhar_copy,
            photo=photo,
            gst_certificate=gst_certificate,
            authorization_letter=authorization_letter,
            company_pan=company_pan
        )

        # === Send Email to Applicant ===
        if email:
            subject_user = "Fusiontec - Application Received"
            message_user = f"""
Dear {name},

Thank you for submitting your DSC application to Fusiontec.
We have received your details and will get in touch with you if needed.

Regards,
Fusiontec Team
"""
            send_mail(subject_user, message_user, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

        # === Send Email to Admin ===
        subject_admin = f"New Applicant Submission: {name}"
        message_admin = f"""
A new applicant form has been submitted:

Name: {name}
Mobile: {mobile_number}
Email: {email}
Reference: {reference}
Reference Contact: {reference_contact}
"""

        send_mail(
            subject_admin,
            message_admin,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_FORM_RECIPIENT],
            fail_silently=False
        )

        return render(request, 'products/type_of_dsc.html', {'success': True})

    return render(request, 'products/type_of_dsc.html')

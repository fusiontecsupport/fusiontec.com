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
from django.contrib.auth.decorators import login_required
from .models import EmudhraPriceListSubmission, biz_product, Fusiontec_product, Fusiontec_Software, Fusiontec_Service, Biz_Service, Biz_Plan

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
            if val is None or val == '':
                return 0.0
            try:
                from decimal import Decimal
                return Decimal(str(val))
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

# ============================================================================
# CUSTOM ADMIN PANEL VIEWS (Without Django Admin)
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login
from .models import (
    ContactSubmission, TallyPriceListSubmission, EmudhraPriceListSubmission,
    FusiontecPriceListSubmission, BizPriceListSubmission, RazorpayTransactionForm,
    RazorpayInfo, CompanyPaymentInfoQR, BankTransferInfo, Applicant,
    Tally_1, Emudhra_2, Fusiontec_3, Biz_4
)

def custom_admin_login(request):
    """Custom admin login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'products/admin/login.html')

@login_required
def custom_admin_dashboard(request):
    """Custom admin dashboard"""
    # Get counts for dashboard
    contact_count = ContactSubmission.objects.count()
    tally_count = TallyPriceListSubmission.objects.count()
    emudhra_count = EmudhraPriceListSubmission.objects.count()
    fusiontec_count = FusiontecPriceListSubmission.objects.count()
    biz_count = BizPriceListSubmission.objects.count()
    payment_count = RazorpayTransactionForm.objects.count()
    applicant_count = Applicant.objects.count()
    
    # Recent submissions
    recent_contacts = ContactSubmission.objects.order_by('-submitted_at')[:5]
    recent_payments = RazorpayTransactionForm.objects.order_by('-created_at')[:5]
    
    context = {
        'contact_count': contact_count,
        'tally_count': tally_count,
        'emudhra_count': emudhra_count,
        'fusiontec_count': fusiontec_count,
        'biz_count': biz_count,
        'payment_count': payment_count,
        'applicant_count': applicant_count,
        'recent_contacts': recent_contacts,
        'recent_payments': recent_payments,
    }
    return render(request, 'products/admin/dashboard.html', context)

@login_required
def custom_admin_contacts(request):
    """Custom admin for contact submissions"""
    search_query = request.GET.get('search', '')
    contacts = ContactSubmission.objects.all()
    
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(contacts.order_by('-submitted_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/contacts.html', context)

@login_required
def custom_admin_tally_submissions(request):
    """Custom admin for Tally submissions"""
    search_query = request.GET.get('search', '')
    submissions = TallyPriceListSubmission.objects.all()
    
    if search_query:
        submissions = submissions.filter(
            Q(customer_name__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(product_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(submissions.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/tally_submissions.html', context)

@login_required
def custom_admin_emudhra_submissions(request):
    """Custom admin for e-Mudhra submissions"""
    search_query = request.GET.get('search', '')
    submissions = EmudhraPriceListSubmission.objects.all()
    
    if search_query:
        submissions = submissions.filter(
            Q(customer_name__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(product_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(submissions.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/emudhra_submissions.html', context)

@login_required
def custom_admin_fusiontec_submissions(request):
    """Custom admin for Fusiontec submissions"""
    search_query = request.GET.get('search', '')
    submissions = FusiontecPriceListSubmission.objects.all()
    
    if search_query:
        submissions = submissions.filter(
            Q(customer_name__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(product_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(submissions.order_by('-submitted_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/fusiontec_submissions.html', context)

@login_required
def custom_admin_biz_submissions(request):
    """Custom admin for Biz submissions"""
    search_query = request.GET.get('search', '')
    submissions = BizPriceListSubmission.objects.all()
    
    if search_query:
        submissions = submissions.filter(
            Q(customer_name__icontains=search_query) |
            Q(mobile__icontains=search_query) |
            Q(product_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(submissions.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/biz_submissions.html', context)

@login_required
def custom_admin_payments(request):
    """Custom admin for payment transactions"""
    search_query = request.GET.get('search', '')
    payments = RazorpayTransactionForm.objects.all()
    
    if search_query:
        payments = payments.filter(
            Q(customer_name__icontains=search_query) |
            Q(razorpay_payment_id__icontains=search_query) |
            Q(razorpay_order_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(payments.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/payments.html', context)

@login_required
def custom_admin_applicants(request):
    """Custom admin for applicant submissions"""
    search_query = request.GET.get('search', '')
    applicants = Applicant.objects.all()
    
    if search_query:
        applicants = applicants.filter(
            Q(name__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(applicants.order_by('-submitted_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/applicants.html', context)

@login_required
def custom_admin_products(request):
    """Custom admin for product management"""
    tally_products = Tally_1.objects.all()
    emudhra_products = Emudhra_2.objects.all()
    fusiontec_products = Fusiontec_3.objects.all()
    biz_products = Biz_4.objects.all()
    
    context = {
        'tally_products': tally_products,
        'emudhra_products': emudhra_products,
        'fusiontec_products': fusiontec_products,
        'biz_products': biz_products,
    }
    return render(request, 'products/admin/products.html', context)

@login_required
def custom_admin_settings(request):
    """Custom admin for payment settings"""
    razorpay_info = RazorpayInfo.objects.all()
    qr_info = CompanyPaymentInfoQR.objects.all()
    bank_info = BankTransferInfo.objects.all()
    
    context = {
        'razorpay_info': razorpay_info,
        'qr_info': qr_info,
        'bank_info': bank_info,
    }
    return render(request, 'products/admin/settings.html', context)

# Custom Edit Views for Products
@login_required
def edit_tally_product(request, product_id):
    """Custom edit view for Tally_1 products"""
    product = get_object_or_404(Tally_1, id=product_id)
    
    if request.method == 'POST':
        product.tally_name = request.POST.get('tally_name')
        product.tally_description = request.POST.get('tally_description')
        product.tally_link = request.POST.get('tally_link')
        
        if 'tally_image' in request.FILES:
            product.tally_image = request.FILES['tally_image']
        
        product.save()
        messages.success(request, 'Tally product updated successfully!')
        return redirect('custom_admin_products')
    
    context = {
        'product': product,
    }
    return render(request, 'products/admin/edit_tally_product.html', context)

@login_required
def edit_emudhra_product(request, product_id):
    """Custom edit view for Emudhra_2 products"""
    product = get_object_or_404(Emudhra_2, id=product_id)
    
    if request.method == 'POST':
        product.emudhra_name = request.POST.get('emudhra_name')
        product.emudhra_description = request.POST.get('emudhra_description')
        product.emudhra_link = request.POST.get('emudhra_link')
        
        if 'emudhra_image' in request.FILES:
            product.emudhra_image = request.FILES['emudhra_image']
        
        product.save()
        messages.success(request, 'e-Mudhra product updated successfully!')
        return redirect('custom_admin_products')
    
    context = {
        'product': product,
    }
    return render(request, 'products/admin/edit_emudhra_product.html', context)

@login_required
def edit_fusiontec_product(request, product_id):
    """Custom edit view for Fusiontec_3 products"""
    product = get_object_or_404(Fusiontec_3, id=product_id)
    
    if request.method == 'POST':
        product.fusiontec_name = request.POST.get('fusiontec_name')
        product.fusiontec_description = request.POST.get('fusiontec_description')
        product.fusiontec_link = request.POST.get('fusiontec_link')
        
        if 'fusiontec_image' in request.FILES:
            product.fusiontec_image = request.FILES['fusiontec_image']
        
        product.save()
        messages.success(request, 'FusionTec product updated successfully!')
        return redirect('custom_admin_products')
    
    context = {
        'product': product,
    }
    return render(request, 'products/admin/edit_fusiontec_product.html', context)

@login_required
def edit_biz_product(request, product_id):
    """Custom edit view for Biz_4 products"""
    product = get_object_or_404(Biz_4, id=product_id)
    
    if request.method == 'POST':
        product.biz_name = request.POST.get('biz_name')
        product.biz_description = request.POST.get('biz_description')
        product.biz_link = request.POST.get('biz_link')
        
        if 'biz_image' in request.FILES:
            product.biz_image = request.FILES['biz_image']
        
        product.save()
        messages.success(request, 'Business Analyst product updated successfully!')
        return redirect('custom_admin_products')
    
    context = {
        'product': product,
    }
    return render(request, 'products/admin/edit_biz_product.html', context)

# Custom Add Views for Products
@login_required
def add_tally_product(request):
    """Custom add view for Tally_1 products"""
    if request.method == 'POST':
        product = Tally_1()
        product.tally_name = request.POST.get('tally_name')
        product.tally_description = request.POST.get('tally_description')
        product.tally_link = request.POST.get('tally_link')
        
        if 'tally_image' in request.FILES:
            product.tally_image = request.FILES['tally_image']
        
        product.save()
        messages.success(request, 'Tally product added successfully!')
        return redirect('custom_admin_products')
    
    return render(request, 'products/admin/add_tally_product.html')

@login_required
def add_emudhra_product(request):
    """Custom add view for Emudhra_2 products"""
    if request.method == 'POST':
        product = Emudhra_2()
        product.emudhra_name = request.POST.get('emudhra_name')
        product.emudhra_description = request.POST.get('emudhra_description')
        product.emudhra_link = request.POST.get('emudhra_link')
        
        if 'emudhra_image' in request.FILES:
            product.emudhra_image = request.FILES['emudhra_image']
        
        product.save()
        messages.success(request, 'e-Mudhra product added successfully!')
        return redirect('custom_admin_products')
    
    return render(request, 'products/admin/add_emudhra_product.html')

@login_required
def add_fusiontec_product(request):
    """Custom add view for Fusiontec_3 products"""
    if request.method == 'POST':
        product = Fusiontec_3()
        product.fusiontec_name = request.POST.get('fusiontec_name')
        product.fusiontec_description = request.POST.get('fusiontec_description')
        product.fusiontec_link = request.POST.get('fusiontec_link')
        
        if 'fusiontec_image' in request.FILES:
            product.fusiontec_image = request.FILES['fusiontec_image']
        
        product.save()
        messages.success(request, 'FusionTec product added successfully!')
        return redirect('custom_admin_products')
    
    return render(request, 'products/admin/add_fusiontec_product.html')

@login_required
def add_biz_product(request):
    """Custom add view for Biz_4 products"""
    if request.method == 'POST':
        product = Biz_4.objects.create(
            biz_name=request.POST.get('biz_name'),
            biz_description=request.POST.get('biz_description'),
            biz_link=request.POST.get('biz_link'),
        )
        
        if 'biz_image' in request.FILES:
            product.biz_image = request.FILES['biz_image']
            product.save()
        
        messages.success(request, 'Business Analyst product added successfully!')
        return redirect('custom_admin_products')
    
    return render(request, 'products/admin/add_biz_product.html')

# Custom RazorpayInfo Admin Views
@login_required
def edit_razorpay_info(request, info_id):
    """Custom edit view for RazorpayInfo"""
    razorpay_info = get_object_or_404(RazorpayInfo, id=info_id)
    
    if request.method == 'POST':
        razorpay_info.title = request.POST.get('title')
        razorpay_info.description = request.POST.get('description')
        razorpay_info.payment_button_id = request.POST.get('payment_button_id')
        razorpay_info.save()
        
        messages.success(request, 'Razorpay settings updated successfully!')
        return redirect('custom_admin_settings')
    
    context = {
        'razorpay_info': razorpay_info,
    }
    return render(request, 'products/admin/edit_razorpay_info.html', context)

@login_required
def add_razorpay_info(request):
    """Custom add view for RazorpayInfo"""
    if request.method == 'POST':
        RazorpayInfo.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            payment_button_id=request.POST.get('payment_button_id'),
        )
        
        messages.success(request, 'Razorpay settings added successfully!')
        return redirect('custom_admin_settings')
    
    return render(request, 'products/admin/add_razorpay_info.html')

# Custom CompanyPaymentInfoQR Admin Views
@login_required
def edit_qr_info(request, info_id):
    """Custom edit view for CompanyPaymentInfoQR"""
    qr_info = get_object_or_404(CompanyPaymentInfoQR, id=info_id)
    
    if request.method == 'POST':
        qr_info.company_name = request.POST.get('company_name')
        qr_info.upi_id = request.POST.get('upi_id')
        
        if 'qr_image' in request.FILES:
            qr_info.qr_image = request.FILES['qr_image']
        
        qr_info.save()
        messages.success(request, 'QR code settings updated successfully!')
        return redirect('custom_admin_settings')
    
    context = {
        'qr_info': qr_info,
    }
    return render(request, 'products/admin/edit_qr_info.html', context)

@login_required
def add_qr_info(request):
    """Custom add view for CompanyPaymentInfoQR"""
    if request.method == 'POST':
        qr_info = CompanyPaymentInfoQR.objects.create(
            company_name=request.POST.get('company_name'),
            upi_id=request.POST.get('upi_id'),
        )
        
        if 'qr_image' in request.FILES:
            qr_info.qr_image = request.FILES['qr_image']
            qr_info.save()
        
        messages.success(request, 'QR code settings added successfully!')
        return redirect('custom_admin_settings')
    
    return render(request, 'products/admin/add_qr_info.html')

# Custom BankTransferInfo Admin Views
@login_required
def edit_bank_info(request, info_id):
    """Custom edit view for BankTransferInfo"""
    bank_info = get_object_or_404(BankTransferInfo, id=info_id)
    
    if request.method == 'POST':
        bank_info.title = request.POST.get('title')
        bank_info.account_name = request.POST.get('account_name')
        bank_info.account_number = request.POST.get('account_number')
        bank_info.ifsc_code = request.POST.get('ifsc_code')
        bank_info.bank_name = request.POST.get('bank_name')
        bank_info.save()
        
        messages.success(request, 'Bank transfer settings updated successfully!')
        return redirect('custom_admin_settings')
    
    context = {
        'bank_info': bank_info,
    }
    return render(request, 'products/admin/edit_bank_info.html', context)

@login_required
def add_bank_info(request):
    """Custom add view for BankTransferInfo"""
    if request.method == 'POST':
        BankTransferInfo.objects.create(
            title=request.POST.get('title'),
            account_name=request.POST.get('account_name'),
            account_number=request.POST.get('account_number'),
            ifsc_code=request.POST.get('ifsc_code'),
            bank_name=request.POST.get('bank_name'),
        )
        
        messages.success(request, 'Bank transfer settings added successfully!')
        return redirect('custom_admin_settings')
    
    return render(request, 'products/admin/add_bank_info.html')

# Custom Views for Managing Related Tally Items
@login_required
def manage_tally_products(request, product_id):
    """Manage related products for a Tally product"""
    tally_product = get_object_or_404(Tally_1, id=product_id)
    related_products = tally_product.products.all()
    
    if request.method == 'POST':
        # Add new product
        Tally_Product.objects.create(
            tally_1=tally_product,
            type_name=request.POST.get('type_name'),
            basic_amount=request.POST.get('basic_amount'),
            cgst=request.POST.get('cgst', 0),
            sgst=request.POST.get('sgst', 0),
        )
        messages.success(request, 'Product added successfully!')
        return redirect('manage_tally_products', product_id=product_id)
    
    context = {
        'tally_product': tally_product,
        'related_products': related_products,
    }
    return render(request, 'products/admin/manage_tally_products.html', context)

@login_required
def manage_tally_services(request, product_id):
    """Manage related services for a Tally product"""
    tally_product = get_object_or_404(Tally_1, id=product_id)
    related_services = tally_product.services.all()
    
    if request.method == 'POST':
        # Add new service
        Tally_Software_Service.objects.create(
            tally_1=tally_product,
            type_name=request.POST.get('type_name'),
            basic_amount=request.POST.get('basic_amount'),
            cgst=request.POST.get('cgst', 0),
            sgst=request.POST.get('sgst', 0),
        )
        messages.success(request, 'Service added successfully!')
        return redirect('manage_tally_services', product_id=product_id)
    
    context = {
        'tally_product': tally_product,
        'related_services': related_services,
    }
    return render(request, 'products/admin/manage_tally_services.html', context)

@login_required
def manage_tally_upgrades(request, product_id):
    """Manage related upgrades for a Tally product"""
    tally_product = get_object_or_404(Tally_1, id=product_id)
    related_upgrades = tally_product.upgrades.all()
    
    if request.method == 'POST':
        # Add new upgrade
        Tally_Upgrade.objects.create(
            tally_1=tally_product,
            type_name=request.POST.get('type_name'),
            basic_amount=request.POST.get('basic_amount'),
            cgst=request.POST.get('cgst', 0),
            sgst=request.POST.get('sgst', 0),
        )
        messages.success(request, 'Upgrade added successfully!')
        return redirect('manage_tally_upgrades', product_id=product_id)
    
    context = {
        'tally_product': tally_product,
        'related_upgrades': related_upgrades,
    }
    return render(request, 'products/admin/manage_tally_upgrades.html', context)

# Delete related items
@login_required
def delete_tally_product_item(request, item_id, item_type):
    """Delete a related product, service, or upgrade"""
    if item_type == 'product':
        item = get_object_or_404(Tally_Product, id=item_id)
        product_id = item.tally_1.id
        item.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('manage_tally_products', product_id=product_id)
    elif item_type == 'service':
        item = get_object_or_404(Tally_Software_Service, id=item_id)
        product_id = item.tally_1.id
        item.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('manage_tally_services', product_id=product_id)
    elif item_type == 'upgrade':
        item = get_object_or_404(Tally_Upgrade, id=item_id)
        product_id = item.tally_1.id
        item.delete()
        messages.success(request, 'Upgrade deleted successfully!')
        return redirect('manage_tally_upgrades', product_id=product_id)

# Unified Product Management System
@login_required
def manage_product_items(request, product_type, product_id):
    """Unified view for managing related items for any product type"""
    
    # Define product type mappings
    product_mappings = {
        'tally': {
            'model': Tally_1,
            'related_models': {
                'products': Tally_Product,
                'services': Tally_Software_Service,
                'upgrades': Tally_Upgrade
            },
            'foreign_key': 'tally_1',
            'name_field': 'tally_name'
        },
        'emudhra': {
            'model': Emudhra_2,
            'related_models': {
                'products': Emudhra_product
            },
            'foreign_key': 'emudhra_2',
            'name_field': 'emudhra_name'
        },
        'fusiontec': {
            'model': Fusiontec_3,
            'related_models': {
                'products': Fusiontec_product,
                'software': Fusiontec_Software,
                'services': Fusiontec_Service
            },
            'foreign_key': 'fusiontec_3',
            'name_field': 'fusiontec_name'
        },
        'biz': {
            'model': Biz_4,
            'related_models': {
                'products': biz_product,
                'services': Biz_Service,
                'plans': Biz_Plan
            },
            'foreign_key': 'biz_4',
            'name_field': 'biz_name'
        }
    }
    
    if product_type not in product_mappings:
        messages.error(request, 'Invalid product type')
        return redirect('custom_admin_products')
    
    config = product_mappings[product_type]
    main_product = get_object_or_404(config['model'], id=product_id)
    
    # Get the item type to manage (products, services, upgrades)
    item_type = request.GET.get('type', 'products')
    if item_type not in config['related_models']:
        item_type = 'products'
    
    related_model = config['related_models'][item_type]
    related_items = related_model.objects.filter(**{config['foreign_key']: main_product})
    
    if request.method == 'POST':
        # Create new item
        item_data = {
            config['foreign_key']: main_product,
        }
        
        # Helper function to safely convert to Decimal
        def to_decimal(value, default=0):
            if value is None or value == '':
                return default
            try:
                from decimal import Decimal
                return Decimal(str(value))
            except (ValueError, TypeError):
                return default

        # Handle different field names for different models
        if product_type == 'tally':
            if item_type == 'products':
                item_data.update({
                    'type_name': request.POST.get('type_name'),
                    'basic_amount': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                })
            elif item_type == 'services':
                item_data.update({
                    'type_name': request.POST.get('type_name'),
                    'basic_amount': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                })
            elif item_type == 'upgrades':
                item_data.update({
                    'type_name': request.POST.get('type_name'),
                    'basic_amount': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                })
        elif product_type == 'emudhra':
            item_data.update({
                'class_product': request.POST.get('type_name'),
                'basic_amount': to_decimal(request.POST.get('basic_amount')),
                'cgst': to_decimal(request.POST.get('cgst')),
                'sgst': to_decimal(request.POST.get('sgst')),
            })
        elif product_type == 'fusiontec':
            if item_type == 'products':
                item_data.update({
                    'fusiontec_product': request.POST.get('type_name'),
                })
            elif item_type == 'software':
                item_data.update({
                    'software_name': request.POST.get('type_name'),
                    'software_description': request.POST.get('description', ''),
                    'basic_amount': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                })
            elif item_type == 'services':
                item_data.update({
                    'service_name': request.POST.get('type_name'),
                    'service_description': request.POST.get('description', ''),
                    'basic_amount': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                })
        elif product_type == 'biz':
            if item_type == 'products':
                item_data.update({
                    'team_name': request.POST.get('type_name'),
                    'old_price': to_decimal(request.POST.get('old_price')),
                    'new_price': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                    'billing_cycle': request.POST.get('billing_cycle', 'Billed for 1 Year | Per Device'),
                })
            elif item_type == 'services':
                item_data.update({
                    'service_name': request.POST.get('type_name'),
                    'service_description': request.POST.get('description', ''),
                    'basic_amount': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                    'billing_cycle': request.POST.get('billing_cycle', 'Billed for 1 Year | Per Device'),
                })
            elif item_type == 'plans':
                item_data.update({
                    'plan_name': request.POST.get('type_name'),
                    'plan_description': request.POST.get('description', ''),
                    'old_price': to_decimal(request.POST.get('old_price')),
                    'new_price': to_decimal(request.POST.get('basic_amount')),
                    'cgst': to_decimal(request.POST.get('cgst')),
                    'sgst': to_decimal(request.POST.get('sgst')),
                    'billing_cycle': request.POST.get('billing_cycle', 'Billed for 1 Year | Per Device'),
                })
        
        related_model.objects.create(**item_data)
        messages.success(request, f'{item_type.title().rstrip("s")} added successfully!')
        return redirect('manage_product_items', product_type=product_type, product_id=product_id)
    
    # Calculate counts for all available types
    type_counts = {}
    for type_name in config['related_models'].keys():
        model = config['related_models'][type_name]
        type_counts[type_name] = model.objects.filter(**{config['foreign_key']: main_product}).count()
    
    context = {
        'product_type': product_type,
        'product_id': product_id,
        'main_product': main_product,
        'item_type': item_type,
        'related_items': related_items,
        'config': config,
        'available_types': list(config['related_models'].keys()),
        'type_counts': type_counts,
    }
    
    return render(request, 'products/admin/manage_product_items.html', context)

@login_required
def delete_product_item(request, product_type, item_id, item_type):
    """Delete a related item for any product type"""
    
    product_mappings = {
        'tally': {
            'products': Tally_Product,
            'services': Tally_Software_Service,
            'upgrades': Tally_Upgrade
        },
        'emudhra': {
            'products': Emudhra_product
        },
        'fusiontec': {
            'products': Fusiontec_product,
            'software': Fusiontec_Software,
            'services': Fusiontec_Service
        },
        'biz': {
            'products': biz_product,
            'services': Biz_Service,
            'plans': Biz_Plan
        }
    }
    
    if product_type not in product_mappings or item_type not in product_mappings[product_type]:
        messages.error(request, 'Invalid product type or item type')
        return redirect('custom_admin_products')
    
    model = product_mappings[product_type][item_type]
    item = get_object_or_404(model, id=item_id)
    
    # Get the main product ID for redirect
    if product_type == 'tally':
        product_id = item.tally_1.id
    elif product_type == 'emudhra':
        product_id = item.emudhra_2.id
    elif product_type == 'fusiontec':
        product_id = item.fusiontec_3.id
    elif product_type == 'biz':
        product_id = item.biz_4.id
    
    item.delete()
    messages.success(request, f'{item_type.title().rstrip("s")} deleted successfully!')
    return redirect('manage_product_items', product_type=product_type, product_id=product_id)

@login_required
def edit_product_item(request, product_type, item_id, item_type):
    """Edit a related item for any product type"""
    
    # Define product type mappings
    product_mappings = {
        'tally': {
            'model': Tally_1,
            'related_models': {
                'products': Tally_Product,
                'services': Tally_Software_Service,
                'upgrades': Tally_Upgrade
            },
            'foreign_key': 'tally_1',
            'name_field': 'tally_name'
        },
        'emudhra': {
            'model': Emudhra_2,
            'related_models': {
                'products': Emudhra_product
            },
            'foreign_key': 'emudhra_2',
            'name_field': 'emudhra_name'
        },
        'fusiontec': {
            'model': Fusiontec_3,
            'related_models': {
                'products': Fusiontec_product,
                'software': Fusiontec_Software,
                'services': Fusiontec_Service
            },
            'foreign_key': 'fusiontec_3',
            'name_field': 'fusiontec_name'
        },
        'biz': {
            'model': Biz_4,
            'related_models': {
                'products': biz_product,
                'services': Biz_Service,
                'plans': Biz_Plan
            },
            'foreign_key': 'biz_4',
            'name_field': 'biz_name'
        }
    }
    
    if product_type not in product_mappings:
        messages.error(request, 'Invalid product type')
        return redirect('custom_admin_products')
    
    config = product_mappings[product_type]
    
    if item_type not in config['related_models']:
        messages.error(request, 'Invalid item type')
        return redirect('custom_admin_products')
    
    related_model = config['related_models'][item_type]
    item = get_object_or_404(related_model, id=item_id)
    
    if request.method == 'POST':
        # Helper function to safely convert to Decimal
        def to_decimal(value, default=0):
            if value is None or value == '':
                return default
            try:
                from decimal import Decimal
                return Decimal(str(value))
            except (ValueError, TypeError):
                return default

        # Update item based on product type and item type
        if product_type == 'tally':
            if item_type == 'products':
                item.type_name = request.POST.get('type_name')
                item.basic_amount = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
            elif item_type == 'services':
                item.type_name = request.POST.get('type_name')
                item.basic_amount = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
            elif item_type == 'upgrades':
                item.type_name = request.POST.get('type_name')
                item.basic_amount = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
        elif product_type == 'emudhra':
            item.class_product = request.POST.get('type_name')
            item.basic_amount = to_decimal(request.POST.get('basic_amount'))
            item.cgst = to_decimal(request.POST.get('cgst'))
            item.sgst = to_decimal(request.POST.get('sgst'))
        elif product_type == 'fusiontec':
            if item_type == 'products':
                item.fusiontec_product = request.POST.get('type_name')
            elif item_type == 'software':
                item.software_name = request.POST.get('type_name')
                item.software_description = request.POST.get('description', '')
                item.basic_amount = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
            elif item_type == 'services':
                item.service_name = request.POST.get('type_name')
                item.service_description = request.POST.get('description', '')
                item.basic_amount = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
        elif product_type == 'biz':
            if item_type == 'products':
                item.team_name = request.POST.get('type_name')
                item.old_price = to_decimal(request.POST.get('old_price'))
                item.new_price = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
                item.billing_cycle = request.POST.get('billing_cycle', 'Billed for 1 Year | Per Device')
            elif item_type == 'services':
                item.service_name = request.POST.get('type_name')
                item.service_description = request.POST.get('description', '')
                item.basic_amount = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
                item.billing_cycle = request.POST.get('billing_cycle', 'Billed for 1 Year | Per Device')
            elif item_type == 'plans':
                item.plan_name = request.POST.get('type_name')
                item.plan_description = request.POST.get('description', '')
                item.old_price = to_decimal(request.POST.get('old_price'))
                item.new_price = to_decimal(request.POST.get('basic_amount'))
                item.cgst = to_decimal(request.POST.get('cgst'))
                item.sgst = to_decimal(request.POST.get('sgst'))
                item.billing_cycle = request.POST.get('billing_cycle', 'Billed for 1 Year | Per Device')
        
        item.save()
        messages.success(request, f'{item_type.title().rstrip("s")} updated successfully!')
        
        # Get the main product ID for redirect
        main_product_id = getattr(item, config['foreign_key']).id
        return redirect('manage_product_items', product_type=product_type, product_id=main_product_id)
    
    # Get the main product for context
    main_product = getattr(item, config['foreign_key'])
    
    context = {
        'product_type': product_type,
        'item_type': item_type,
        'item': item,
        'main_product': main_product,
        'config': config,
    }
    
    return render(request, 'products/admin/edit_product_item.html', context)

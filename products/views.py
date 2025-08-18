from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.core.mail.backends.smtp import EmailBackend
import time
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
import json

from .models import (
    ProductMaster, ProductType, ProductItem, RateCardMaster, Customer, 
    QuoteSubmission, ContactSubmission, PaymentTransaction, 
    PaymentSettings, Applicant,
    ProductTypeMaster, ProductMasterV2, RateCardEntry,
    ProductFormSubmission, DscPrice,
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def admin_required(view_func):
    """Custom decorator to check if admin is logged in via session"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('admin_logged_in', False):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/admin-login/')
    return _wrapped_view

# ============================================================================
# HOME PAGE & PRODUCT CATALOG
# ============================================================================

def index(request):
    """Home page with contact form and product showcase"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, phone, subject, message]):
            messages.error(request, 'Please fill out all required fields.')
            return redirect('index')

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

    # Get active products for showcase using new database structure
    product_masters = ProductMaster.objects.filter(is_active=True).order_by('display_order')
    
    # Get product type masters for the new structure
    product_type_masters = ProductTypeMaster.objects.all().order_by('id')
    
    # Get payment information
    razorpay_infos = PaymentSettings.objects.filter(setting_type='razorpay', is_active=True)
    payment_infos = PaymentSettings.objects.filter(setting_type='qr_code', is_active=True)
    bank_infos = PaymentSettings.objects.filter(setting_type='bank_transfer', is_active=True)
    
    context = {
        'product_masters': product_masters,
        'product_type_masters': product_type_masters,
        'razorpay_infos': razorpay_infos,
        'payment_infos': payment_infos,
        'bank_infos': bank_infos,
    }
    return render(request, 'products/index.html', context)

def product_catalog(request):
    """Product catalog page showing all products"""
    product_masters = ProductMaster.objects.filter(is_active=True).order_by('display_order')
    
    # Get search query
    search_query = request.GET.get('search', '')
    if search_query:
        product_items = ProductItem.objects.filter(
            Q(item_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(features__icontains=search_query),
            is_active=True
        ).select_related('product_type', 'product_type__product_master')
    else:
        product_items = ProductItem.objects.filter(
            is_active=True
        ).select_related('product_type', 'product_type__product_master')
    
    # Pagination
    paginator = Paginator(product_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'product_masters': product_masters,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/catalog.html', context)

def product_detail(request, product_id):
    """Individual product detail page"""
    product_item = get_object_or_404(ProductItem, id=product_id, is_active=True)
    
    # Get related products from same type
    related_items = ProductItem.objects.filter(
        product_type=product_item.product_type,
        is_active=True
    ).exclude(id=product_id)[:4]
    
    context = {
        'product_item': product_item,
        'related_items': related_items,
    }
    return render(request, 'products/product_detail.html', context)

def product_type_products(request, type_id):
    """Show all products under a specific product type"""
    product_type = get_object_or_404(ProductType, id=type_id, is_active=True)
    product_items = ProductItem.objects.filter(
        product_type=product_type,
        is_active=True
    ).order_by('display_order')
    
    context = {
        'product_type': product_type,
        'product_items': product_items,
    }
    return render(request, 'products/product_type.html', context)

def product_type_form(request, type_id):
    """Display product form for a specific product type"""
    product_type = get_object_or_404(ProductTypeMaster, id=type_id)
    
    # Get all available products for this type
    available_products = ProductMasterV2.objects.filter(product_type=product_type)
    
    # Get the first available product item for this type, or create a dummy one
    try:
        product_item = available_products.first()
        if not product_item:
            # Create a dummy product item for display purposes
            product_item = type('DummyProduct', (), {
                'prdt_desc': product_type.prdt_desc,
                'basic_amount': 0,
                'cgst': 0,
                'sgst': 0,
                'token_amount': 0,
                'installing_charges': 0
            })()
    except:
        product_item = type('DummyProduct', (), {
            'prdt_desc': product_type.prdt_desc,
            'basic_amount': 0,
            'cgst': 0,
            'sgst': 0,
            'token_amount': 0,
            'installing_charges': 0
        })()
    
    # Get rate card data for each product
    products_with_rates = []
    for product in available_products:
        # Get the latest rate card for this product
        latest_rate = RateCardEntry.objects.filter(product=product).order_by('-rate_date').first()
        
        if latest_rate:
            products_with_rates.append({
                'product': product,
                'rate_card': latest_rate
            })
        else:
            # If no rate card, create a default one
            products_with_rates.append({
                'product': product,
                'rate_card': type('DefaultRate', (), {
                    'base_amt': 0,
                    'cgst': 0,
                    'sgst': 0,
                    'token_amount': 0,
                    'installation_charge': 0
                })()
            })
    
    # Debug: Print what we're getting
    print(f"Debug: Found {len(products_with_rates)} products with rates")
    for pw in products_with_rates:
        print(f"Product: {pw['product'].prdt_desc}, Rate: {pw['rate_card']}")
    
    context = {
        'product': product_item,
        'product_type': product_type,
        'available_products': available_products,
        'products_with_rates': products_with_rates,
    }
    return render(request, 'products/product_form.html', context)

def dsc_form(request):
    """Dedicated DSC landing/form page similar to eMudhra's buy page."""
    return render(request, 'products/dsc_form.html')

def dsc_price_api(request):
    """Return price for a DSC combination.
    Params: class_type, user_type, cert_type, validity, outside (0/1)
    """
    class_type = request.GET.get('class_type', 'class3')
    user_type = request.GET.get('user_type', 'individual')
    cert_type = request.GET.get('cert_type', 'signature')
    validity = request.GET.get('validity', '2y')
    outside = request.GET.get('outside', '0') == '1'

    try:
        def canonical(val: str) -> str:
            val = (val or '').lower()
            return ''.join(ch for ch in val if ch.isalnum())

        requested = canonical(class_type)

        qs = DscPrice.objects.filter(
            user_type=user_type,
            cert_type=cert_type,
            validity=validity,
            is_active=True,
        )

        price_row = None
        for row in qs:
            if canonical(row.class_type) == requested:
                price_row = row
                break
        if price_row is None and requested in {'class3','classiii','class3dsc'}:
            for row in qs:
                if canonical(row.class_type) in {'class3','classiii','class3dsc'}:
                    price_row = row
                    break
        if price_row is None and qs.count() == 1:
            price_row = qs.first()
        if price_row is None:
            return JsonResponse({'success': False, 'message': 'Price not configured for this selection'}, status=404)

        price = float(price_row.nett_amount)
        if outside:
            price += float(price_row.outside_india_surcharge or 0)
        return JsonResponse({
            'success': True,
            'price': price,
            'currency': 'INR',
            'components': {
                'dsc_charge': float(price_row.dsc_charge),
                'token_amount': float(price_row.token_amount),
                'installation_charge': float(price_row.installation_charge),
                'gst_percent': float(price_row.gst_percent),
            },
            'outside_surcharge': float(price_row.outside_india_surcharge or 0)
        })
    except DscPrice.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Price not configured'}, status=404)
    except Exception as e:
        # Handle cases like missing table before migrations
        return JsonResponse({'success': False, 'message': f'Pricing backend not ready: {str(e)}'}, status=404)

def dsc_options_api(request):
    """Return available DSC combinations for building dynamic buttons.
    Structure:
    {
      classes: ["class3", "dgft", ...],
      map: { class: { user_type: { cert_type: ["1y","2y",...] } } },
      defaults: { class_type, user_type, cert_type, validity }
    }
    """
    try:
        options = {}
        classes = []
        default_row = None
        for row in DscPrice.objects.filter(is_active=True).order_by('created_at'):
            if default_row is None:
                default_row = row
            c = row.class_type
            u = row.user_type
            t = row.cert_type
            v = row.validity
            if c not in options:
                options[c] = {}
                classes.append(c)
            if u not in options[c]:
                options[c][u] = {}
            if t not in options[c][u]:
                options[c][u][t] = []
            if v not in options[c][u][t]:
                options[c][u][t].append(v)
        if not classes:
            return JsonResponse({'success': True, 'classes': [], 'map': {}, 'defaults': {} })
        defaults = {
            'class_type': default_row.class_type,
            'user_type': default_row.user_type,
            'cert_type': default_row.cert_type,
            'validity': default_row.validity,
        }
        return JsonResponse({'success': True, 'classes': classes, 'map': options, 'defaults': defaults})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def dsc_enquiry_api(request):
    """Create a DSC enquiry from the landing page."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    try:
        payload = json.loads(request.body or '{}')
    except Exception:
        payload = request.POST
    try:
        name = (payload.get('name') or '').strip()
        email = (payload.get('email') or '').strip()
        mobile = (payload.get('mobile') or '').strip()
        address = (payload.get('address') or '').strip() or None
        class_type = payload.get('class_type')
        user_type = payload.get('user_type')
        cert_type = payload.get('cert_type')
        validity = payload.get('validity')
        include_token = bool(payload.get('include_token'))
        include_installation = bool(payload.get('include_installation'))
        outside_india = bool(payload.get('outside_india'))
        quoted_price = float(payload.get('quoted_price') or 0)

        if not (name and email and mobile):
            return JsonResponse({'success': False, 'message': 'Name, Email and Mobile are required.'}, status=400)

        from .models import DscEnquiry
        enquiry = DscEnquiry.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            address=address,
            class_type=class_type or '',
            user_type=user_type or '',
            cert_type=cert_type or '',
            validity=validity or '',
            include_token=include_token,
            include_installation=include_installation,
            outside_india=outside_india,
            quoted_price=quoted_price,
        )
        return JsonResponse({'success': True, 'id': enquiry.id})
    except Exception as exc:
        return JsonResponse({'success': False, 'message': str(exc)}, status=500)

@admin_required
def custom_admin_dsc_enquiries(request):
    """List DSC enquiries in custom admin."""
    from .models import DscEnquiry
    enquiries = DscEnquiry.objects.all().order_by('-created_at')
    paginator = Paginator(enquiries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'products/admin/dsc_enquiries.html', context)

@csrf_exempt
def save_product_submission(request):
    """Save product submission to database"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create or get customer
            customer, created = Customer.objects.get_or_create(
                email=data.get('email'),
                defaults={
                    'name': data.get('customer_name'),
                    'company_name': data.get('company_name', ''),
                    'mobile': data.get('mobile'),
                    'has_gst': data.get('has_gst') == 'yes',
                    'gst_number': data.get('gst_number', ''),
                    'address': data.get('address', ''),
                    'state': data.get('state', ''),
                    'district': data.get('district', ''),
                    'pincode': data.get('pincode', ''),
                }
            )
            
            # Update customer if not created
            if not created:
                customer.name = data.get('customer_name')
                customer.company_name = data.get('company_name', '')
                customer.mobile = data.get('mobile')
                customer.has_gst = data.get('has_gst') == 'yes'
                customer.gst_number = data.get('gst_number', '')
                customer.address = data.get('address', '')
                customer.state = data.get('state', '')
                customer.district = data.get('district', '')
                customer.pincode = data.get('pincode', '')
                customer.save()
            
            # Get product item
            product_item = ProductMasterV2.objects.get(id=data.get('product_id'))
            
            # Calculate GST rates from amounts
            basic_amount = data.get('basic_amount', 0)
            cgst_amount = data.get('cgst', 0)
            sgst_amount = data.get('sgst', 0)
            
            # Calculate GST rates (avoid division by zero)
            cgst_rate = 0
            sgst_rate = 0
            if basic_amount > 0:
                cgst_rate = (cgst_amount / basic_amount) * 100
                sgst_rate = (sgst_amount / basic_amount) * 100
            
            # Save to the new ProductFormSubmission table
            form_submission = ProductFormSubmission.objects.create(
                customer_name=data.get('customer_name'),
                company_name=data.get('company_name', ''),
                mobile=data.get('mobile'),
                email=data.get('email'),
                has_gst=data.get('has_gst'),
                gst_number=data.get('gst_number', ''),
                address=data.get('address', ''),
                state=data.get('state', ''),
                district=data.get('district', ''),
                pincode=data.get('pincode', ''),
                product_id=product_item,
                quantity=data.get('quantity', 1),
                basic_amount=basic_amount,
                cgst_rate=cgst_rate,
                sgst_rate=sgst_rate,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                total_with_gst=data.get('total_amount', 0),
                token_amount=data.get('token_amount', 0),
                installation_charges=data.get('installing_charges', 0),
                grand_total=data.get('grand_total', 0),
                status='new'
            )
            
            # Send admin notification email
            admin_email_content = render_to_string('products/product_form_email.html', {
                'customer_name': data.get('customer_name'),
                'company_name': data.get('company_name', ''),
                'email': data.get('email'),
                'mobile': data.get('mobile'),
                'has_gst': data.get('has_gst'),
                'gst_number': data.get('gst_number', ''),
                'address': data.get('address', ''),
                'state': data.get('state', ''),
                'district': data.get('district', ''),
                'pincode': data.get('pincode', ''),
                'product_name': product_item.prdt_desc,
                'quantity': data.get('quantity', 1),
                'basic_amount': basic_amount,
                'cgst_amount': cgst_amount,
                'sgst_amount': sgst_amount,
                'total_with_gst': data.get('total_amount', 0),
                'token_amount': data.get('token_amount', 0),
                'installation_charges': data.get('installing_charges', 0),
                'grand_total': data.get('grand_total', 0),
                'submission_id': form_submission.id,
            })

            # Send customer thank you email
            customer_thank_you_content = render_to_string('products/product_form_thanks.html', {
                'customer_name': data.get('customer_name'),
                'product_name': product_item.prdt_desc,
                'quantity': data.get('quantity', 1),
                'submission_id': form_submission.id,
            })

            try:
                # Send to admin
                admin_email = EmailMessage(
                    subject=f"[Fusiontec Product Form] - {product_item.prdt_desc} - {data.get('customer_name')}",
                    body=admin_email_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_FORM_RECIPIENT],
                )
                admin_email.content_subtype = "html"
                admin_email.send()

                # Send thank you to customer
                customer_email = EmailMessage(
                    subject="Product Form Submission Received - Fusiontec",
                    body=customer_thank_you_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[data.get('email')],
                )
                customer_email.content_subtype = "html"
                customer_email.send()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Form submitted successfully! You will receive a confirmation email shortly.',
                    'form_submission_id': form_submission.id
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'success',
                    'message': f'Form submitted successfully but there was an error sending confirmation emails: {str(e)}',
                    'form_submission_id': form_submission.id
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error saving submission: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# ============================================================================
# QUOTE & CONTACT FORMS
# ============================================================================

def quote_form(request, product_id):
    """Quote request form for a specific product"""
    product_item = get_object_or_404(ProductItem, id=product_id, is_active=True)
    
    if request.method == 'POST':
        # Handle quote form submission
        customer_name = request.POST.get('customer_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        quantity = int(request.POST.get('quantity', 1))
        
        if not all([customer_name, email, mobile]):
            messages.error(request, 'Please fill out all required fields.')
            return redirect('quote_form', product_id=product_id)
        
        # Create or get customer
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                'name': customer_name,
                'company_name': company_name,
                'mobile': mobile,
            }
        )
        
        # Calculate pricing
        basic_amount = product_item.basic_amount * quantity
        cgst = product_item.cgst * quantity
        sgst = product_item.sgst * quantity
        total_amount = basic_amount + cgst + sgst
        token_amount = product_item.token_amount or 0
        installing_charges = product_item.installing_charges or 0
        grand_total = total_amount + token_amount + installing_charges
        
        # Create quote submission
        quote = QuoteSubmission.objects.create(
            customer=customer,
            product_item=product_item,
            quantity=quantity,
            basic_amount=basic_amount,
            cgst=cgst,
            sgst=sgst,
            total_amount=total_amount,
            token_amount=token_amount,
            installing_charges=installing_charges,
            grand_total=grand_total,
            status='pending'
        )
        
        # Send admin notification email
        admin_email_content = render_to_string('products/quote_form_email.html', {
            'customer_name': customer_name,
            'company_name': company_name,
            'email': email,
            'mobile': mobile,
            'product_name': product_item.item_name,
            'quantity': quantity,
            'basic_amount': basic_amount,
            'cgst': cgst,
            'sgst': sgst,
            'total_amount': total_amount,
            'token_amount': token_amount,
            'installing_charges': installing_charges,
            'grand_total': grand_total,
            'quote_id': quote.id,
        })

        # Send customer thank you email
        customer_thank_you_content = render_to_string('products/quote_form_thanks.html', {
            'customer_name': customer_name,
            'product_name': product_item.item_name,
            'quantity': quantity,
            'quote_id': quote.id,
        })

        try:
            # Send to admin
            admin_email = EmailMessage(
                subject=f"[Fusiontec Quote Request] - {product_item.item_name} - {customer_name}",
                body=admin_email_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_FORM_RECIPIENT],
            )
            admin_email.content_subtype = "html"
            admin_email.send()

            # Send thank you to customer
            customer_email = EmailMessage(
                subject="Quote Request Received - Fusiontec",
                body=customer_thank_you_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            customer_email.content_subtype = "html"
            customer_email.send()

            messages.success(request, 'Quote request submitted successfully! You will receive a confirmation email shortly.')
        except Exception as e:
            messages.error(request, f'Quote submitted but there was an error sending confirmation emails: {str(e)}')
        
        return redirect('quote_detail', quote_id=quote.id)
    
    context = {
        'product_item': product_item,
    }
    return render(request, 'products/quote_form.html', context)

def quote_detail(request, quote_id):
    """Show quote details"""
    quote = get_object_or_404(QuoteSubmission, id=quote_id)
    
    context = {
        'quote': quote,
    }
    return render(request, 'products/quote_detail.html', context)

def contact_form(request):
    """Contact form page"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, phone, subject, message]):
            messages.error(request, 'Please fill out all required fields.')
            return redirect('contact_form')

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

            messages.success(request, 'Your message has been sent successfully! You will receive a confirmation email shortly.')
        except Exception as e:
            messages.error(request, f'Message saved but there was an error sending confirmation emails: {str(e)}')

        # Redirect back to the referring page or home page
        referer = request.META.get('HTTP_REFERER')
        if referer and 'contact' not in referer:
            return redirect(referer)
        else:
            return redirect('index')
    
    # If it's a GET request, redirect to home page
    return redirect('index')

def submit_quote(request):
    """Handle quote form submission and send email using stored credentials"""
    if request.method == 'POST':
        try:
            # Get form data
            customer_name = request.POST.get('customer_name', '').strip()
            company_name = request.POST.get('company_name', '').strip()
            mobile = request.POST.get('mobile', '').strip()
            email = request.POST.get('email', '').strip()
            gst_number = request.POST.get('gst_number', '').strip()
            address = request.POST.get('address', '').strip()
            state = request.POST.get('state', '').strip()
            district = request.POST.get('district', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            product_type_id = request.POST.get('product_type_id')
            quantity = int(request.POST.get('quantity', 1))
            additional_requirements = request.POST.get('additional_requirements', '').strip()
            
            print(f"=== QUOTE FORM DEBUG ===")
            print(f"Customer: {customer_name}")
            print(f"Email: {email}")
            print(f"Product Type ID: {product_type_id}")
            print(f"All POST data: {dict(request.POST)}")
            
            # Validate required fields
            if not all([customer_name, mobile, email, product_type_id]):
                messages.error(request, 'Please fill all required fields.')
                return redirect('index')
            
            # Get product type details
            try:
                product_type = ProductTypeMaster.objects.get(id=product_type_id)
                print(f"Found product type: {product_type.prdt_desc}")
                print(f"Email configured: {product_type.sender_email}")
                print(f"App password configured: {'Yes' if product_type.app_password else 'No'}")
            except ProductTypeMaster.DoesNotExist:
                messages.error(request, 'Product type not found.')
                return redirect('index')
            
            # Create submission record
            print("Creating submission record...")
            try:
                from django.utils import timezone
                from .models import QuoteRequest
                
                # Create quote request record
                quote_request = QuoteRequest.objects.create(
                    customer_name=customer_name,
                    company_name=company_name,
                    mobile=mobile,
                    email=email,
                    product_type=product_type,
                    quantity=quantity,
                    address=address,
                    state=state,
                    district=district,
                    pincode=pincode,
                    gst_number=gst_number if gst_number else None,
                    additional_requirements=additional_requirements,
                    status='new'
                )
                print(f"Quote request created with ID: {quote_request.id}")
            except Exception as e:
                print(f"Error creating quote request: {e}")
                print(f"Error type: {type(e).__name__}")
                raise e
            
            # Send email if email credentials are configured
            print(f"Checking email credentials: sender_email='{product_type.sender_email}', app_password='{'Yes' if product_type.app_password else 'No'}'")
            if product_type.sender_email and product_type.app_password:
                print(f"Attempting to send email from {product_type.sender_email} to {email}")
                try:
                    # Configure email backend with stored credentials
                    email_backend = EmailBackend(
                        host='smtp.gmail.com',
                        port=587,
                        username=product_type.sender_email,
                        password=product_type.app_password,
                        use_tls=True,
                        fail_silently=False
                    )
                    print("Email backend configured successfully")
                    
                    # Prepare email content
                    subject = f"Quote Request - {product_type.prdt_desc}"
                    
                    # Create email body
                    email_body = f"""
Dear {customer_name},

Thank you for your quote request for {product_type.prdt_desc}.

Your request details:
- Product Type: {product_type.prdt_desc}
- Quantity: {quantity}
- Company: {company_name or 'Not specified'}
- Contact: {mobile}
- Email: {email}
- Address: {address}
- State: {state}
- District: {district}
- Pincode: {pincode}
- GST Number: {gst_number or 'Not provided'}
- Additional Requirements: {additional_requirements or 'None'}

Our team will review your requirements and get back to you with a detailed quote within 24-48 hours.

Best regards,
FusionTec Team
                    """
                    
                    # Send email to customer using custom backend
                    print("Creating customer email message...")
                    email_message = EmailMessage(
                        subject=subject,
                        body=email_body,
                        from_email=product_type.sender_email,
                        to=[email],
                        reply_to=[product_type.sender_email]
                    )
                    email_message.connection = email_backend
                    print("Sending customer email...")
                    email_message.send()
                    print("Customer email sent successfully!")
                    
                    # Send notification to admin
                    print("Creating admin notification email...")
                    admin_subject = f"New Quote Request - {product_type.prdt_desc}"
                    admin_body = f"""
New quote request received:

Customer: {customer_name}
Product Type: {product_type.prdt_desc}
Quantity: {quantity}
Contact: {mobile} | {email}
Company: {company_name or 'Not specified'}

Additional Requirements:
{additional_requirements or 'None'}

Quote Request ID: {quote_request.id}
                    """
                    
                    admin_email = EmailMessage(
                        subject=admin_subject,
                        body=admin_body,
                        from_email=product_type.sender_email,
                        to=[product_type.sender_email]  # Send to admin email
                    )
                    admin_email.connection = email_backend
                    print("Sending admin email...")
                    admin_email.send()
                    print("Admin email sent successfully!")
                    
                    print(f"All emails sent successfully from {product_type.sender_email} to {email}")
                    
                    # Update email status
                    quote_request.email_sent = True
                    quote_request.email_sent_at = timezone.now()
                    quote_request.save()
                    print(f"Email status updated for quote request #{quote_request.id}")
                    
                    messages.success(request, 'Quote request submitted successfully! We will contact you soon.')
                    
                except Exception as email_error:
                    # Log the email error but don't fail the submission
                    print(f"Email sending failed: {email_error}")
                    print(f"Email credentials: {product_type.sender_email}")
                    messages.success(request, 'Quote request submitted successfully! We will contact you soon.')
            else:
                # No email credentials configured, just show success message
                print(f"No email credentials configured for product type: {product_type.prdt_desc}")
                messages.success(request, 'Quote request submitted successfully! We will contact you soon.')
            
            return redirect('index')
            
        except Exception as e:
            messages.error(request, f'Error submitting quote: {str(e)}')
            return redirect('index')
    
    return redirect('index')

# ============================================================================
# ADMIN FUNCTIONS
# ============================================================================

def custom_admin_logout(request):
    """Admin logout function"""
    if 'admin_logged_in' in request.session:
        del request.session['admin_logged_in']
    if 'admin_username' in request.session:
        del request.session['admin_username']
    messages.success(request, "Logout successfully")
    return redirect('/')

def custom_admin_login(request):
    """Admin login function"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Simple admin check (you should implement proper authentication)
        if username == 'admin' and password == 'admin':
            request.session['admin_logged_in'] = True
            request.session['admin_username'] = username
            messages.success(request, 'Login successful!')
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'products/admin/login.html')

@admin_required
def custom_admin_dashboard(request):
    """Admin dashboard with comprehensive data"""
    from django.db.models import Count, Sum, Q
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Get current date and calculate date ranges
    now = timezone.now()
    today = now.date()
    this_month = now.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Basic counts
    total_customers = Customer.objects.count()
    total_quotes = QuoteSubmission.objects.count()
    total_contacts = ContactSubmission.objects.count()
    total_products = ProductMasterV2.objects.count()
    
    # Monthly statistics
    this_month_quotes = QuoteSubmission.objects.filter(
        created_at__gte=this_month
    ).count()
    this_month_contacts = ContactSubmission.objects.filter(
        created_at__gte=this_month
    ).count()
    this_month_customers = Customer.objects.filter(
        created_at__gte=this_month
    ).count()
    
    last_month_quotes = QuoteSubmission.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    last_month_contacts = ContactSubmission.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    last_month_customers = Customer.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month
    ).count()
    
    # Calculate growth percentages
    quote_growth = ((this_month_quotes - last_month_quotes) / max(last_month_quotes, 1)) * 100 if last_month_quotes > 0 else 0
    contact_growth = ((this_month_contacts - last_month_contacts) / max(last_month_contacts, 1)) * 100 if last_month_contacts > 0 else 0
    customer_growth = ((this_month_customers - last_month_customers) / max(last_month_customers, 1)) * 100 if last_month_customers > 0 else 0
    
    # Quote status distribution
    quote_status_counts = QuoteSubmission.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Product performance (top products by quote count)
    top_products = QuoteSubmission.objects.values(
        'product_item__item_name'
    ).annotate(
        quote_count=Count('id'),
        total_amount=Sum('grand_total')
    ).order_by('-quote_count')[:5]
    
    # Recent activities (last 7 days)
    week_ago = now - timedelta(days=7)
    recent_quotes = QuoteSubmission.objects.select_related(
        'customer', 'product_item'
    ).filter(
        created_at__gte=week_ago
    ).order_by('-created_at')[:10]
    
    recent_contacts = ContactSubmission.objects.filter(
        created_at__gte=week_ago
    ).order_by('-created_at')[:10]
    
    # Today's activities
    today_quotes = QuoteSubmission.objects.filter(
        created_at__date=today
    ).count()
    today_contacts = ContactSubmission.objects.filter(
        created_at__date=today
    ).count()
    today_customers = Customer.objects.filter(
        created_at__date=today
    ).count()
    
    # Revenue statistics
    total_revenue = QuoteSubmission.objects.filter(
        status='approved'
    ).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    
    this_month_revenue = QuoteSubmission.objects.filter(
        status='approved',
        created_at__gte=this_month
    ).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    
    last_month_revenue = QuoteSubmission.objects.filter(
        status='approved',
        created_at__gte=last_month,
        created_at__lt=this_month
    ).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    
    revenue_growth = ((this_month_revenue - last_month_revenue) / max(last_month_revenue, 1)) * 100 if last_month_revenue > 0 else 0
    
    # Customer location distribution (top states)
    top_states = Customer.objects.exclude(
        state__isnull=True
    ).exclude(
        state=''
    ).values('state').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Weekly trend data for charts
    weekly_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        day_quotes = QuoteSubmission.objects.filter(
            created_at__date=date
        ).count()
        day_contacts = ContactSubmission.objects.filter(
            created_at__date=date
        ).count()
        weekly_data.append({
            'date': date.strftime('%b %d'),
            'quotes': day_quotes,
            'contacts': day_contacts
        })
    weekly_data.reverse()
    
    context = {
        # Basic counts
        'total_customers': total_customers,
        'total_quotes': total_quotes,
        'total_contacts': total_contacts,
        'total_products': total_products,
        
        # Monthly statistics
        'this_month_quotes': this_month_quotes,
        'this_month_contacts': this_month_contacts,
        'this_month_customers': this_month_customers,
        
        # Growth percentages
        'quote_growth': round(quote_growth, 1),
        'contact_growth': round(contact_growth, 1),
        'customer_growth': round(customer_growth, 1),
        
        # Quote status distribution
        'quote_status_counts': quote_status_counts,
        
        # Top products
        'top_products': top_products,
        
        # Recent activities
        'recent_quotes': recent_quotes,
        'recent_contacts': recent_contacts,
        
        # Today's activities
        'today_quotes': today_quotes,
        'today_contacts': today_contacts,
        'today_customers': today_customers,
        
        # Revenue statistics
        'total_revenue': total_revenue,
        'this_month_revenue': this_month_revenue,
        'revenue_growth': round(revenue_growth, 1),
        
        # Location data
        'top_states': top_states,
        
        # Chart data
        'weekly_data': weekly_data,
        
        # Chart data for enhanced dashboard
        'monthly_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'monthly_quotes': [this_month_quotes, last_month_quotes, 0, 0, 0, 0],
        'monthly_contacts': [this_month_contacts, last_month_contacts, 0, 0, 0, 0],
        'product_labels': ['Tally', 'e-Mudhra', 'FusionTec', 'Business'],
        'product_data': [25, 30, 20, 25],
        'revenue_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'revenue_data': [this_month_revenue, last_month_revenue, 0, 0, 0, 0],
        
        # Date info
        'today': today.strftime('%B %d, %Y'),
        'this_month': this_month.strftime('%B %Y'),
    }
    return render(request, 'products/admin/dashboard.html', context)


@admin_required
def dashboard_data_api(request):
    """API endpoint for dashboard data updates"""
    from django.http import JsonResponse
    from django.db.models import Count, Sum, Q
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Get current date and calculate date ranges
    now = timezone.now()
    today = now.date()
    this_month = now.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Basic counts
    total_customers = Customer.objects.count()
    total_quotes = QuoteSubmission.objects.count()
    total_contacts = ContactSubmission.objects.count()
    total_products = ProductMasterV2.objects.count()
    
    # Monthly statistics
    this_month_quotes = QuoteSubmission.objects.filter(
        created_at__gte=this_month
    ).count()
    this_month_contacts = ContactSubmission.objects.filter(
        created_at__gte=this_month
    ).count()
    
    # Recent activities
    recent_quotes = QuoteSubmission.objects.select_related('customer').order_by('-created_at')[:5]
    recent_contacts = ContactSubmission.objects.order_by('-created_at')[:5]
    
    # Format recent activities
    recent_quotes_data = []
    for quote in recent_quotes:
        recent_quotes_data.append({
            'title': f"Quote from {quote.customer.name}",
            'time': quote.created_at.strftime('%b %d, %H:%M'),
            'icon': 'file-invoice'
        })
    
    recent_contacts_data = []
    for contact in recent_contacts:
        recent_contacts_data.append({
            'title': f"Contact from {contact.name}",
            'time': contact.created_at.strftime('%b %d, %H:%M'),
            'icon': 'envelope'
        })
    
    data = {
        'total_customers': total_customers,
        'total_quotes': total_quotes,
        'total_contacts': total_contacts,
        'total_products': total_products,
        'this_month_quotes': this_month_quotes,
        'this_month_contacts': this_month_contacts,
        'recent_quotes': recent_quotes_data,
        'recent_contacts': recent_contacts_data,
    }
    
    return JsonResponse(data)

@admin_required
def custom_admin_contacts(request):
    """Admin contacts management"""
    contacts = ContactSubmission.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'products/admin/contacts.html', context)

@admin_required
def custom_admin_quotes(request):
    """Admin quotes management"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            quote_id = request.POST.get('quote_id')
            new_status = request.POST.get('status')
            notes = request.POST.get('notes', '')
            
            try:
                quote = QuoteSubmission.objects.get(id=quote_id)
                quote.status = new_status
                quote.notes = notes
                quote.save()
                messages.success(request, f'Quote #{quote_id} status updated to {new_status}.')
            except QuoteSubmission.DoesNotExist:
                messages.error(request, 'Quote not found.')
            except Exception as e:
                messages.error(request, f'Failed to update quote: {e}')
            
            return redirect('custom_admin_quotes')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status_filter', '')
    
    # Build queryset with select_related for performance
    quotes = QuoteSubmission.objects.select_related(
        'customer', 
        'product_item__product_type__product_master'
    ).all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        quotes = quotes.filter(
            models.Q(customer__name__icontains=search_query) |
            models.Q(customer__mobile__icontains=search_query) |
            models.Q(customer__email__icontains=search_query) |
            models.Q(product_item__item_name__icontains=search_query) |
            models.Q(product_item__product_type__type_name__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter:
        quotes = quotes.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(quotes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'products/admin/quotes.html', context)

@admin_required
def custom_admin_products(request):
    """Admin management for the NEW simple product tables.

    - Create ProductTypeMaster (if form_type = 'type')
    - Create ProductMasterV2 (if form_type = 'product')
    - Edit/Delete functionality
    """
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        action = request.POST.get('action')
        
        try:
            if action == 'delete_type':
                type_id = request.POST.get('type_id')
                ProductTypeMaster.objects.get(id=type_id).delete()
                messages.success(request, 'Product Type deleted.')
                return redirect('custom_admin_products')
            elif action == 'delete_product':
                product_id = request.POST.get('product_id')
                ProductMasterV2.objects.get(id=product_id).delete()
                messages.success(request, 'Product deleted.')
                return redirect('custom_admin_products')
            elif form_type == 'edit_type':
                type_id = request.POST.get('type_id')
                prdt_desc = (request.POST.get('prdt_desc') or '').strip()
                image = request.FILES.get('image')
                sender_email = (request.POST.get('sender_email') or '').strip()
                app_password = (request.POST.get('app_password') or '').strip()
                
                if not type_id or not prdt_desc:
                    messages.error(request, 'Type ID and description are required.')
                else:
                    try:
                        product_type = ProductTypeMaster.objects.get(id=int(type_id))
                        product_type.prdt_desc = prdt_desc
                        product_type.sender_email = sender_email if sender_email else None
                        product_type.app_password = app_password if app_password else None
                        if image:
                            product_type.image = image
                        product_type.save()
                        messages.success(request, 'Product Type updated.')
                    except ProductTypeMaster.DoesNotExist:
                        messages.error(request, 'Product Type not found.')
                    except Exception as exc:
                        messages.error(request, f'Failed to update: {exc}')
                return redirect('custom_admin_products')
            elif form_type == 'type':
                prdt_desc = (request.POST.get('prdt_desc') or '').strip()
                image = request.FILES.get('image')
                sender_email = (request.POST.get('sender_email') or '').strip()
                app_password = (request.POST.get('app_password') or '').strip()
                if not prdt_desc:
                    messages.error(request, 'Type description is required.')
                else:
                    ProductTypeMaster.objects.create(
                        prdt_desc=prdt_desc, 
                        image=image,
                        sender_email=sender_email if sender_email else None,
                        app_password=app_password if app_password else None
                    )
                    messages.success(request, 'Product Type created.')
                    return redirect('custom_admin_products')
            elif form_type == 'product':
                type_id = request.POST.get('product_type')
                prdt_desc = (request.POST.get('prdt_desc') or '').strip()
                if not type_id or not prdt_desc:
                    messages.error(request, 'Type and Product description are required.')
                else:
                    pt = ProductTypeMaster.objects.get(id=int(type_id))
                    ProductMasterV2.objects.create(product_type=pt, prdt_desc=prdt_desc)
                    messages.success(request, 'Product created.')
                    return redirect('custom_admin_products')
        except Exception as exc:
            messages.error(request, f'Failed to save: {exc}')

    types = ProductTypeMaster.objects.all().order_by('id')
    
    # Handle filtering by product type
    selected_type = request.GET.get('type_filter', '')
    products = ProductMasterV2.objects.select_related('product_type').all().order_by('id')
    
    print(f"DEBUG: selected_type = '{selected_type}', type = {type(selected_type)}")
    
    if selected_type:
        try:
            products = products.filter(product_type_id=int(selected_type))
            print(f"DEBUG: Filtered products count: {products.count()}")
        except (ValueError, TypeError) as e:
            print(f"DEBUG: Filter error: {e}")
            # If conversion fails, don't filter
            pass

    context = {
        'simple_types': types,
        'simple_products': products,
        'selected_type': selected_type,
    }
    return render(request, 'products/admin/products.html', context)

@admin_required
def admin_product_types(request, master_id):
    """Deprecated in new schema: keep route for compatibility (no-op redirect)."""
    return redirect('custom_admin_products')

    if request.method == 'POST':
        type_code = (request.POST.get('type_code') or '').strip()
        type_name = (request.POST.get('type_name') or '').strip()
        description = (request.POST.get('description') or '').strip()
        is_active = request.POST.get('is_active') == 'on'
        display_order = request.POST.get('display_order') or '0'

        if not type_code or not type_name:
            messages.error(request, 'Type Code and Type Name are required.')
        else:
            try:
                ProductType.objects.create(
                    product_master=master,
                    type_code=type_code,
                    type_name=type_name,
                    description=description or None,
                    is_active=is_active,
                    display_order=int(display_order),
                )
                messages.success(request, 'Product type created successfully.')
                return redirect('admin_product_types', master_id=master.id)
            except Exception as exc:
                messages.error(request, f'Failed to create product type: {exc}')

    types_qs = master.product_types.all().order_by('display_order', 'type_name')
    context = {
        'master': master,
        'types': types_qs,
    }
    return render(request, 'products/admin/product_types.html', context)

@admin_required
def admin_product_items(request, type_id):
    """Deprecated in new schema: keep route for compatibility (no-op redirect)."""
    return redirect('custom_admin_products')

    if request.method == 'POST':
        item_code = (request.POST.get('item_code') or '').strip()
        item_name = (request.POST.get('item_name') or '').strip()
        item_category = (request.POST.get('item_category') or 'product').strip()
        description = (request.POST.get('description') or '').strip()
        features = (request.POST.get('features') or '').strip()
        is_active = request.POST.get('is_active') == 'on'
        display_order = int((request.POST.get('display_order') or '0').strip())

        # pricing
        def to_decimal(val):
            try:
                return None if val is None or val == '' else float(val)
            except Exception:
                return None

        basic_amount = to_decimal(request.POST.get('basic_amount'))
        cgst = to_decimal(request.POST.get('cgst')) or 0
        sgst = to_decimal(request.POST.get('sgst')) or 0
        token_name = (request.POST.get('token_name') or '').strip() or None
        token_amount = to_decimal(request.POST.get('token_amount'))
        installing_charges = to_decimal(request.POST.get('installing_charges'))
        billing_cycle = (request.POST.get('billing_cycle') or '').strip() or None
        old_price = to_decimal(request.POST.get('old_price'))

        if not item_code or not item_name:
            messages.error(request, 'Item Code and Item Name are required.')
        else:
            try:
                ProductItem.objects.create(
                    product_type=ptype,
                    item_code=item_code,
                    item_name=item_name,
                    item_category=item_category,
                    description=description or None,
                    features=features or None,
                    is_active=is_active,
                    display_order=display_order,
                    basic_amount=basic_amount,
                    cgst=cgst,
                    sgst=sgst,
                    token_name=token_name,
                    token_amount=token_amount,
                    installing_charges=installing_charges,
                    billing_cycle=billing_cycle,
                    old_price=old_price,
                )
                messages.success(request, 'Product item created successfully.')
                return redirect('admin_product_items', type_id=ptype.id)
            except Exception as exc:
                messages.error(request, f'Failed to create item: {exc}')

    items = ptype.product_items.all().order_by('display_order', 'item_name')
    context = {
        'ptype': ptype,
        'items': items,
    }
    return render(request, 'products/admin/product_items.html', context)

@admin_required
def admin_rate_cards(request, item_id):
    """New schema: manage rate cards for ProductMasterV2 by ID."""
    product = get_object_or_404(ProductMasterV2, id=item_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete_rate':
            rate_id = request.POST.get('rate_id')
            try:
                RateCardEntry.objects.get(id=rate_id).delete()
                messages.success(request, 'Rate card deleted.')
                return redirect('admin_rate_cards', item_id=product.id)
            except Exception as exc:
                messages.error(request, f'Failed to delete rate card: {exc}')
        elif action == 'edit_rate':
            # Handle edit - smart editing based on date
            rate_id = request.POST.get('rate_id')
            rate_date = (request.POST.get('rate_date') or '').strip()
            base_amount = (request.POST.get('base_amount') or '').strip()
            gst_percent = (request.POST.get('gst_percent') or '').strip()
            
            # Token fields
            token_desc = (request.POST.get('token_desc') or '').strip()
            token_amount = (request.POST.get('token_amount') or '').strip()
            token_gst_percent = (request.POST.get('token_gst_percent') or '').strip()
            
            # Installation fields
            installation_charge = (request.POST.get('installation_charge') or '').strip()
            installation_gst_percent = (request.POST.get('installation_gst_percent') or '').strip()

            from datetime import datetime
            try:
                rate_dt = datetime.strptime(rate_date, '%Y-%m-%d').date()
            except Exception:
                messages.error(request, 'Invalid Rate Date. Use YYYY-MM-DD format.')
                return redirect('admin_rate_cards', item_id=product.id)

            try:
                base_amt = float(base_amount)
                gst_pct = float(gst_percent or 0)
                token_amt = float(token_amount or 0)
                token_gst_pct = float(token_gst_percent or 18)
                install_charge = float(installation_charge or 0)
                install_gst_pct = float(installation_gst_percent or 18)
            except Exception:
                messages.error(request, 'Invalid amounts provided.')
                return redirect('admin_rate_cards', item_id=product.id)

            try:
                # Get the existing rate card entry
                existing_rate = RateCardEntry.objects.get(id=rate_id)
                
                # Check if the date is the same as the original
                if existing_rate.rate_date == rate_dt:
                    # Same date - update the existing entry
                    existing_rate.base_amt = base_amt
                    existing_rate.gst_percent = gst_pct
                    existing_rate.token_desc = token_desc
                    existing_rate.token_amount = token_amt
                    existing_rate.token_gst_percent = token_gst_pct
                    existing_rate.installation_charge = install_charge
                    existing_rate.installation_gst_percent = install_gst_pct
                    existing_rate.save()
                    messages.success(request, 'Rate card updated successfully (same date).')
                else:
                    # Different date - create a new entry for history
                    RateCardEntry.objects.create(
                        product=product,
                        rate_date=rate_dt,
                        base_amt=base_amt,
                        gst_percent=gst_pct,
                        token_desc=token_desc,
                        token_amount=token_amt,
                        token_gst_percent=token_gst_pct,
                        installation_charge=install_charge,
                        installation_gst_percent=install_gst_pct,
                    )
                    messages.success(request, 'Rate card updated successfully (new entry created for new date).')
                
                return redirect('admin_rate_cards', item_id=product.id)
            except RateCardEntry.DoesNotExist:
                messages.error(request, 'Rate card not found.')
                return redirect('admin_rate_cards', item_id=product.id)
            except Exception as exc:
                messages.error(request, f'Failed to update rate card: {exc}')
                return redirect('admin_rate_cards', item_id=product.id)
        else:
            # Handle new rate card creation
            rate_date = (request.POST.get('rate_date') or '').strip()
            base_amount = (request.POST.get('base_amount') or '').strip()
            gst_percent = (request.POST.get('gst_percent') or '').strip()
            
            # Token fields
            token_desc = (request.POST.get('token_desc') or '').strip()
            token_amount = (request.POST.get('token_amount') or '').strip()
            token_gst_percent = (request.POST.get('token_gst_percent') or '').strip()
            
            # Installation fields
            installation_charge = (request.POST.get('installation_charge') or '').strip()
            installation_gst_percent = (request.POST.get('installation_gst_percent') or '').strip()

            from datetime import datetime
            try:
                rate_dt = datetime.strptime(rate_date, '%Y-%m-%d').date()
            except Exception:
                messages.error(request, 'Invalid Rate Date. Use YYYY-MM-DD format.')
                return redirect('admin_rate_cards', item_id=product.id)

            try:
                base_amt = float(base_amount)
                gst_pct = float(gst_percent or 0)
                token_amt = float(token_amount or 0)
                token_gst_pct = float(token_gst_percent or 18)
                install_charge = float(installation_charge or 0)
                install_gst_pct = float(installation_gst_percent or 18)
            except Exception:
                messages.error(request, 'Invalid amounts provided.')
                return redirect('admin_rate_cards', item_id=product.id)

            try:
                RateCardEntry.objects.create(
                    product=product,
                    rate_date=rate_dt,
                    base_amt=base_amt,
                    gst_percent=gst_pct,
                    token_desc=token_desc,
                    token_amount=token_amt,
                    token_gst_percent=token_gst_pct,
                    installation_charge=install_charge,
                    installation_gst_percent=install_gst_pct,
                )
                messages.success(request, 'Rate card added successfully.')
                return redirect('admin_rate_cards', item_id=product.id)
            except Exception as exc:
                messages.error(request, f'Failed to add rate card: {exc}')

    cards = product.rate_cards.all().order_by('-rate_date')
    context = {
        'simple_product': product,
        'cards': cards,
    }
    return render(request, 'products/admin/rate_cards.html', context)

# ============================================================================
# CUSTOM ADMIN VIEWS (Additional)
# ============================================================================

@admin_required
def custom_admin_tally_submissions(request):
    """Custom admin for Tally submissions - DEPRECATED"""
    context = {
        'page_obj': [],
        'search_query': '',
        'deprecated': True,
        'message': 'The old Tally submissions system has been deprecated. Please use the new unified quotes system.'
    }
    return render(request, 'products/admin/tally_submissions.html', context)

@admin_required
def custom_admin_emudhra_submissions(request):
    """Custom admin for e-Mudhra submissions - DEPRECATED"""
    context = {
        'page_obj': [],
        'search_query': '',
        'deprecated': True,
        'message': 'The old e-Mudhra submissions system has been deprecated. Please use the new unified quotes system.'
    }
    return render(request, 'products/admin/emudhra_submissions.html', context)

@admin_required
def custom_admin_fusiontec_submissions(request):
    """Custom admin for Fusiontec submissions - DEPRECATED"""
    context = {
        'page_obj': [],
        'search_query': '',
        'deprecated': True,
        'message': 'The old Fusiontec submissions system has been deprecated. Please use the new unified quotes system.'
    }
    return render(request, 'products/admin/fusiontec_submissions.html', context)

@admin_required
def custom_admin_biz_submissions(request):
    """Custom admin for Business Intelligence submissions"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_submission':
            submission_id = request.POST.get('submission_id')
            try:
                quote = QuoteSubmission.objects.get(id=submission_id)
                quote.delete()
                messages.success(request, f'Quote #{submission_id} deleted successfully.')
            except QuoteSubmission.DoesNotExist:
                messages.error(request, 'Quote not found.')
            except Exception as e:
                messages.error(request, f'Failed to delete quote: {e}')
            
            return redirect('custom_admin_biz_submissions')
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Fetch quotes related to Business Intelligence products
    quotes = QuoteSubmission.objects.select_related(
        'customer', 
        'product_item__product_type__product_master'
    ).filter(
        product_item__product_type__product_master__product_code='biz'
    ).order_by('-created_at')
    
    # Apply search filter
    if search_query:
        quotes = quotes.filter(
            models.Q(customer__name__icontains=search_query) |
            models.Q(customer__mobile__icontains=search_query) |
            models.Q(customer__email__icontains=search_query) |
            models.Q(product_item__item_name__icontains=search_query) |
            models.Q(product_item__product_type__type_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(quotes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/biz_submissions.html', context)

@admin_required
def custom_admin_payments(request):
    """Custom admin for payment transactions"""
    search_query = request.GET.get('search', '')
    from .models import PaymentTransaction
    payments = PaymentTransaction.objects.all()
    
    if search_query:
        payments = payments.filter(
            Q(customer__name__icontains=search_query) |
            Q(razorpay_payment_id__icontains=search_query) |
            Q(razorpay_order_id__icontains=search_query) |
            Q(customer__email__icontains=search_query)
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

@admin_required
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
    paginator = Paginator(applicants.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'products/admin/applicants.html', context)

@admin_required
def custom_admin_settings(request):
    """Custom admin for payment settings"""
    from .models import PaymentSettings
    
    # Get payment settings by type
    razorpay_settings = PaymentSettings.objects.filter(setting_type='razorpay', is_active=True).first()
    qr_settings = PaymentSettings.objects.filter(setting_type='qr_code', is_active=True).first()
    bank_settings = PaymentSettings.objects.filter(setting_type='bank_transfer', is_active=True).first()
    
    context = {
        'razorpay_info': [razorpay_settings] if razorpay_settings else [],
        'qr_info': [qr_settings] if qr_settings else [],
        'bank_info': [bank_settings] if bank_settings else [],
    }
    return render(request, 'products/admin/settings.html', context)

@admin_required
def admin_dsc_prices(request):
    """Admin page to view/update DSC dynamic prices."""
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        row_id = request.POST.get('row_id')
        class_type = request.POST.get('class_type')
        user_type = request.POST.get('user_type')
        cert_type = request.POST.get('cert_type')
        validity = request.POST.get('validity')
        dsc_charge = request.POST.get('dsc_charge')
        token_amount = request.POST.get('token_amount') or '0'
        installation_charge = request.POST.get('installation_charge') or '0'
        gst_percent = request.POST.get('gst_percent') or '18'
        surcharge = request.POST.get('outside_india_surcharge') or '0'
        is_active = request.POST.get('is_active') == 'on'

        try:
            if action == 'delete' and row_id:
                DscPrice.objects.filter(id=row_id).delete()
                messages.success(request, 'Price row deleted.')
                return redirect('admin_dsc_prices')

            if row_id:
                row = DscPrice.objects.get(id=row_id)
                row.class_type = class_type
                row.user_type = user_type
                row.cert_type = cert_type
                row.validity = validity
                row.dsc_charge = float(dsc_charge or 0)
                row.token_amount = float(token_amount or 0)
                row.installation_charge = float(installation_charge or 0)
                row.gst_percent = float(gst_percent or 0)
                row.outside_india_surcharge = float(surcharge or 0)
                row.is_active = is_active
                row.save()
                messages.success(request, 'Price updated.')
            else:
                DscPrice.objects.create(
                    class_type=class_type,
                    user_type=user_type,
                    cert_type=cert_type,
                    validity=validity,
                    dsc_charge=float(dsc_charge or 0),
                    token_amount=float(token_amount or 0),
                    installation_charge=float(installation_charge or 0),
                    gst_percent=float(gst_percent or 0),
                    outside_india_surcharge=float(surcharge or 0),
                    is_active=is_active,
                )
                messages.success(request, 'Price added.')
            return redirect('admin_dsc_prices')
        except Exception as exc:
            messages.error(request, f'Failed to save price: {exc}')

    prices = DscPrice.objects.order_by('class_type','user_type','cert_type','validity')
    context = { 'prices': prices }
    return render(request, 'products/admin/dsc_prices.html', context)

@admin_required
def custom_admin_form_submissions(request):
    """Admin dashboard for product form submissions"""
    submissions = ProductFormSubmission.objects.all().order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    product_filter = request.GET.get('product', '')
    date_filter = request.GET.get('date', '')
    
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    if product_filter:
        submissions = submissions.filter(product_id__id=product_filter)
    
    if date_filter:
        submissions = submissions.filter(created_at__date=date_filter)
    
    # Pagination
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique products for filter
    products = ProductMasterV2.objects.all().order_by('prdt_desc')
    
    # Statistics
    total_submissions = ProductFormSubmission.objects.count()
    new_submissions = ProductFormSubmission.objects.filter(status='new').count()
    reviewed_submissions = ProductFormSubmission.objects.filter(status='reviewed').count()
    approved_submissions = ProductFormSubmission.objects.filter(status='approved').count()
    converted_submissions = ProductFormSubmission.objects.filter(status='converted').count()
    
    context = {
        'page_obj': page_obj,
        'total_submissions': total_submissions,
        'new_submissions': new_submissions,
        'reviewed_submissions': reviewed_submissions,
        'approved_submissions': approved_submissions,
        'converted_submissions': converted_submissions,
        'products': products,
        'status_filter': status_filter,
        'product_filter': product_filter,
        'date_filter': date_filter,
    }
    
    return render(request, 'products/admin/form_submissions.html', context)

@admin_required
def custom_admin_quote_requests(request):
    """Admin dashboard for quote requests"""
    from .models import QuoteRequest
    quote_requests = QuoteRequest.objects.all().order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    product_type_filter = request.GET.get('product_type', '')
    date_filter = request.GET.get('date', '')
    
    if status_filter:
        quote_requests = quote_requests.filter(status=status_filter)
    
    if product_type_filter:
        quote_requests = quote_requests.filter(product_type_id=product_type_filter)
    
    if date_filter:
        quote_requests = quote_requests.filter(created_at__date=date_filter)
    
    # Pagination
    paginator = Paginator(quote_requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique product types for filter
    product_types = ProductTypeMaster.objects.all().order_by('prdt_desc')
    
    # Statistics
    total_requests = QuoteRequest.objects.count()
    new_requests = QuoteRequest.objects.filter(status='new').count()
    reviewed_requests = QuoteRequest.objects.filter(status='reviewed').count()
    quoted_requests = QuoteRequest.objects.filter(status='quoted').count()
    accepted_requests = QuoteRequest.objects.filter(status='accepted').count()
    
    context = {
        'page_obj': page_obj,
        'total_requests': total_requests,
        'new_requests': new_requests,
        'reviewed_requests': reviewed_requests,
        'quoted_requests': quoted_requests,
        'accepted_requests': accepted_requests,
        'product_types': product_types,
        'status_filter': status_filter,
        'product_type_filter': product_type_filter,
        'date_filter': date_filter,
    }
    
    return render(request, 'products/admin/quote_requests.html', context)

@admin_required
def quote_request_detail(request, request_id):
    """API endpoint to get quote request details"""
    from .models import QuoteRequest
    try:
        quote_request = QuoteRequest.objects.get(id=request_id)
        
        # Render the details as HTML
        html_content = f"""
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-primary">Customer Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>Name:</strong></td><td>{quote_request.customer_name}</td></tr>
                    <tr><td><strong>Company:</strong></td><td>{quote_request.company_name or 'Not specified'}</td></tr>
                    <tr><td><strong>Mobile:</strong></td><td>{quote_request.mobile}</td></tr>
                    <tr><td><strong>Email:</strong></td><td>{quote_request.email}</td></tr>
                    <tr><td><strong>GST Number:</strong></td><td>{quote_request.gst_number or 'Not provided'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-primary">Product Information</h6>
                <table class="table table-sm">
                    <tr><td><strong>Product Type:</strong></td><td>{quote_request.product_type.prdt_desc}</td></tr>
                    <tr><td><strong>Quantity:</strong></td><td>{quote_request.quantity}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>
                        <span class="badge bg-{'warning' if quote_request.status == 'new' else 'info' if quote_request.status == 'reviewed' else 'primary' if quote_request.status == 'quoted' else 'success' if quote_request.status == 'accepted' else 'danger' if quote_request.status == 'rejected' else 'secondary'}">
                            {quote_request.status.title()}
                        </span>
                    </td></tr>
                    <tr><td><strong>Created:</strong></td><td>{quote_request.created_at.strftime('%B %d, %Y at %I:%M %p')}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6 class="text-primary">Address Information</h6>
                <p>{quote_request.get_address_info()}</p>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6 class="text-primary">Additional Requirements</h6>
                <p>{quote_request.additional_requirements or 'No additional requirements specified'}</p>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6 class="text-primary">Email Status</h6>
                <table class="table table-sm">
                    <tr><td><strong>Email Sent:</strong></td><td>
                        <span class="badge bg-{'success' if quote_request.email_sent else 'danger'}">
                            <i class="fas fa-{'check' if quote_request.email_sent else 'times'}"></i>
                            {'Sent' if quote_request.email_sent else 'Not Sent'}
                        </span>
                    </td></tr>
                    <tr><td><strong>Sent At:</strong></td><td>{quote_request.email_sent_at.strftime('%B %d, %Y at %I:%M %p') if quote_request.email_sent_at else 'N/A'}</td></tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6 class="text-primary">Admin Notes</h6>
                <textarea class="form-control" rows="3" placeholder="Add admin notes here...">{quote_request.admin_notes or ''}</textarea>
            </div>
        </div>
        """
        
        return JsonResponse({
            'success': True,
            'html': html_content
        })
        
    except QuoteRequest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Quote request not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@admin_required
@csrf_exempt
def update_quote_request_status(request, request_id):
    """API endpoint to update quote request status"""
    from .models import QuoteRequest
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if not new_status:
            return JsonResponse({'success': False, 'message': 'Status is required'}, status=400)
        
        quote_request = QuoteRequest.objects.get(id=request_id)
        quote_request.status = new_status
        quote_request.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {new_status}'
        })
        
    except QuoteRequest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Quote request not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

# ============================================================================
# PRODUCT MANAGEMENT VIEWS (New Structure)
# ============================================================================

@admin_required
def add_fusiontec_product(request):
    """Add new Fusiontec product"""
    from .models import ProductMasterV2
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('add_fusiontec_product')
        
        try:
            product = ProductMasterV2.objects.create(
                name=name,
                description=description,
                product_type='fusiontec'
            )
            
            if image:
                product.image = image
                product.save()
            
            messages.success(request, 'Fusiontec product added successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return render(request, 'products/admin/add_fusiontec_product.html')

@admin_required
def edit_fusiontec_product(request, product_id):
    """Edit Fusiontec product"""
    from .models import ProductMasterV2
    product = get_object_or_404(ProductMasterV2, id=product_id, product_type='fusiontec')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('edit_fusiontec_product', product_id=product_id)
        
        try:
            product.name = name
            product.description = description
            
            if image:
                product.image = image
            
            product.save()
            messages.success(request, 'Fusiontec product updated successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {'product': product}
    return render(request, 'products/admin/edit_fusiontec_product.html', context)

@admin_required
def add_biz_product(request):
    """Add new Biz product"""
    from .models import ProductMasterV2
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('add_biz_product')
        
        try:
            product = ProductMasterV2.objects.create(
                name=name,
                description=description,
                product_type='biz'
            )
            
            if image:
                product.image = image
                product.save()
            
            messages.success(request, 'Biz product added successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return render(request, 'products/admin/add_biz_product.html')

@admin_required
def edit_biz_product(request, product_id):
    """Edit Biz product"""
    from .models import ProductMasterV2
    product = get_object_or_404(ProductMasterV2, id=product_id, product_type='biz')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('edit_biz_product', product_id=product_id)
        
        try:
            product.name = name
            product.description = description
            
            if image:
                product.image = image
            
            product.save()
            messages.success(request, 'Biz product updated successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {'product': product}
    return render(request, 'products/admin/edit_biz_product.html', context)

@admin_required
def add_emudhra_product(request):
    """Add new e-Mudhra product"""
    from .models import ProductMasterV2
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('add_emudhra_product')
        
        try:
            product = ProductMasterV2.objects.create(
                name=name,
                description=description,
                product_type='emudhra'
            )
            
            if image:
                product.image = image
                product.save()
            
            messages.success(request, 'e-Mudhra product added successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return render(request, 'products/admin/add_emudhra_product.html')

@admin_required
def edit_emudhra_product(request, product_id):
    """Edit e-Mudhra product"""
    from .models import ProductMasterV2
    product = get_object_or_404(ProductMasterV2, id=product_id, product_type='emudhra')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('edit_emudhra_product', product_id=product_id)
        
        try:
            product.name = name
            product.description = description
            
            if image:
                product.image = image
            
            product.save()
            messages.success(request, 'e-Mudhra product updated successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {'product': product}
    return render(request, 'products/admin/edit_emudhra_product.html', context)

@admin_required
def add_tally_product(request):
    """Add new Tally product"""
    from .models import ProductMasterV2
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('add_tally_product')
        
        try:
            product = ProductMasterV2.objects.create(
                name=name,
                description=description,
                product_type='tally'
            )
            
            if image:
                product.image = image
                product.save()
            
            messages.success(request, 'Tally product added successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return render(request, 'products/admin/add_tally_product.html')

@admin_required
def edit_tally_product(request, product_id):
    """Edit Tally product"""
    from .models import ProductMasterV2
    product = get_object_or_404(ProductMasterV2, id=product_id, product_type='tally')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'Product name is required.')
            return redirect('edit_tally_product', product_id=product_id)
        
        try:
            product.name = name
            product.description = description
            
            if image:
                product.image = image
            
            product.save()
            messages.success(request, 'Tally product updated successfully.')
            return redirect('custom_admin_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {'product': product}
    return render(request, 'products/admin/edit_tally_product.html', context)

# ============================================================================
# SETTINGS MANAGEMENT VIEWS
# ============================================================================

@admin_required
def edit_razorpay_info(request, info_id):
    """Edit Razorpay payment info"""
    from .models_old import RazorpayInfo
    info = get_object_or_404(RazorpayInfo, id=info_id)
    
    if request.method == 'POST':
        info.key_id = request.POST.get('key_id', '').strip()
        info.key_secret = request.POST.get('key_secret', '').strip()
        info.save()
        messages.success(request, 'Razorpay info updated successfully.')
        return redirect('custom_admin_settings')
    
    context = {'info': info}
    return render(request, 'products/admin/edit_razorpay_info.html', context)

@admin_required
def add_razorpay_info(request):
    """Add new Razorpay payment info"""
    from .models_old import RazorpayInfo
    
    if request.method == 'POST':
        key_id = request.POST.get('key_id', '').strip()
        key_secret = request.POST.get('key_secret', '').strip()
        
        if not key_id or not key_secret:
            messages.error(request, 'Both Key ID and Key Secret are required.')
            return redirect('add_razorpay_info')
        
        RazorpayInfo.objects.create(key_id=key_id, key_secret=key_secret)
        messages.success(request, 'Razorpay info added successfully.')
        return redirect('custom_admin_settings')
    
    return render(request, 'products/admin/add_razorpay_info.html')

@admin_required
def edit_qr_info(request, info_id):
    """Edit QR payment info"""
    from .models_old import CompanyPaymentInfoQR
    info = get_object_or_404(CompanyPaymentInfoQR, id=info_id)
    
    if request.method == 'POST':
        info.qr_code = request.FILES.get('qr_code') or info.qr_code
        info.account_number = request.POST.get('account_number', '').strip()
        info.ifsc_code = request.POST.get('ifsc_code', '').strip()
        info.account_holder_name = request.POST.get('account_holder_name', '').strip()
        info.save()
        messages.success(request, 'QR info updated successfully.')
        return redirect('custom_admin_settings')
    
    context = {'info': info}
    return render(request, 'products/admin/edit_qr_info.html', context)

@admin_required
def add_qr_info(request):
    """Add new QR payment info"""
    from .models_old import CompanyPaymentInfoQR
    
    if request.method == 'POST':
        qr_code = request.FILES.get('qr_code')
        account_number = request.POST.get('account_number', '').strip()
        ifsc_code = request.POST.get('ifsc_code', '').strip()
        account_holder_name = request.POST.get('account_holder_name', '').strip()
        
        if not all([qr_code, account_number, ifsc_code, account_holder_name]):
            messages.error(request, 'All fields are required.')
            return redirect('add_qr_info')
        
        CompanyPaymentInfoQR.objects.create(
            qr_code=qr_code,
            account_number=account_number,
            ifsc_code=ifsc_code,
            account_holder_name=account_holder_name
        )
        messages.success(request, 'QR info added successfully.')
        return redirect('custom_admin_settings')
    
    return render(request, 'products/admin/add_qr_info.html')

@admin_required
def edit_bank_info(request, info_id):
    """Edit bank transfer info"""
    from .models_old import BankTransferInfo
    info = get_object_or_404(BankTransferInfo, id=info_id)
    
    if request.method == 'POST':
        info.bank_name = request.POST.get('bank_name', '').strip()
        info.account_number = request.POST.get('account_number', '').strip()
        info.ifsc_code = request.POST.get('ifsc_code', '').strip()
        info.account_holder_name = request.POST.get('account_holder_name', '').strip()
        info.save()
        messages.success(request, 'Bank info updated successfully.')
        return redirect('custom_admin_settings')
    
    context = {'info': info}
    return render(request, 'products/admin/edit_bank_info.html', context)

@admin_required
def add_bank_info(request):
    """Add new bank transfer info"""
    from .models_old import BankTransferInfo
    
    if request.method == 'POST':
        bank_name = request.POST.get('bank_name', '').strip()
        account_number = request.POST.get('account_number', '').strip()
        ifsc_code = request.POST.get('ifsc_code', '').strip()
        account_holder_name = request.POST.get('account_holder_name', '').strip()
        
        if not all([bank_name, account_number, ifsc_code, account_holder_name]):
            messages.error(request, 'All fields are required.')
            return redirect('add_bank_info')
        
        BankTransferInfo.objects.create(
            bank_name=bank_name,
            account_number=account_number,
            ifsc_code=ifsc_code,
            account_holder_name=account_holder_name
        )
        messages.success(request, 'Bank info added successfully.')
        return redirect('custom_admin_settings')
    
    return render(request, 'products/admin/add_bank_info.html')

# ============================================================================
# API ENDPOINTS
# ============================================================================

@csrf_exempt
def get_states(request):
    """Get list of states for forms"""
    import json
    import os
    from django.conf import settings
    
    # Load states from JSON file
    json_path = os.path.join(settings.BASE_DIR, 'data', 'states_districts.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract state names from the JSON structure
        states = [item['state'] for item in data.get('states', [])]
        return JsonResponse({'states': states})
    except Exception as e:
        print(f"Error loading states: {e}")
        return JsonResponse({'states': []})

@csrf_exempt
def get_districts(request, state):
    """Get districts for a specific state"""
    import json
    import os
    from django.conf import settings
    
    # Load districts from JSON file
    json_path = os.path.join(settings.BASE_DIR, 'data', 'states_districts.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find the state and get its districts
        districts = []
        for item in data.get('states', []):
            if item['state'] == state:
                districts = item.get('districts', [])
                break
        
        return JsonResponse({'districts': districts})
    except Exception as e:
        print(f"Error loading districts: {e}")
        return JsonResponse({'districts': []})

@csrf_exempt
def get_submission_details(request, submission_id):
    """API endpoint to get submission details for modal"""
    try:
        submission = ProductFormSubmission.objects.get(id=submission_id)
        
        # Render the details HTML
        from django.template.loader import render_to_string
        html_content = render_to_string('products/admin/submission_details.html', {
            'submission': submission
        })
        
        return JsonResponse({
            'success': True,
            'html': html_content
        })
        
    except ProductFormSubmission.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Submission not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

@csrf_exempt
def convert_submission_to_quote(request, submission_id):
    """API endpoint to convert submission to quote"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)
    
    try:
        submission = ProductFormSubmission.objects.get(id=submission_id)
        
        if submission.status == 'converted':
            return JsonResponse({
                'success': False,
                'message': 'Submission already converted'
            })
        
        # Convert to quote
        quote = submission.convert_to_quote()
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully converted to quote',
            'quote_id': quote.id
        })
        
    except ProductFormSubmission.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Submission not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error converting: {str(e)}'
        }, status=500)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'products/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'products/500.html', status=500)

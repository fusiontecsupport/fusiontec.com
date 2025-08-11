from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
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
    ProductFormSubmission,
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
            
            return JsonResponse({
                'status': 'success',
                'message': 'Form submitted successfully!',
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
        
        messages.success(request, 'Quote request submitted successfully!')
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

        messages.success(request, 'Your message has been sent successfully.')
        return redirect('contact_form')
    
    return render(request, 'products/contact_form.html')

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
            elif form_type == 'type':
                prdt_desc = (request.POST.get('prdt_desc') or '').strip()
                image = request.FILES.get('image')
                if not prdt_desc:
                    messages.error(request, 'Type description is required.')
                else:
                    ProductTypeMaster.objects.create(prdt_desc=prdt_desc, image=image)
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
    from data.states_districts import states_districts
    
    states = list(states_districts.keys())
    return JsonResponse({'states': states})

@csrf_exempt
def get_districts(request, state):
    """Get districts for a specific state"""
    from data.states_districts import states_districts
    
    districts = states_districts.get(state, [])
    return JsonResponse({'districts': districts})

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

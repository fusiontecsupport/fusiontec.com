from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ProductMaster, ProductType, ProductItem, RateCardMaster, Customer, QuoteSubmission,
    ContactSubmission, PaymentTransaction, PaymentSettings, Applicant,
    ProductTypeMaster, ProductMasterV2, ProductSubMaster, RateCardEntry, ProductFormSubmission, QuoteRequest,
    DscEnquiry, DscSubmission,
)

# ============================================================================
# PRODUCT MASTER ADMIN
# ============================================================================

@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'product_name', 'sender_email', 'is_active', 'display_order', 'get_types_count', 'get_items_count']
    list_filter = ['is_active', 'product_code']
    search_fields = ['product_name', 'description', 'sender_email']
    ordering = ['display_order', 'product_name']
    readonly_fields = ['get_types_count', 'get_items_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_code', 'product_name', 'description', 'is_active', 'display_order')
        }),
        ('Media & Links', {
            'fields': ('image', 'website_link'),
            'classes': ('collapse',)
        }),
        ('Email Configuration', {
            'fields': ('sender_email', 'app_password'),
            'description': 'Email settings for sending notifications for this product'
        }),
    )
    
    def get_types_count(self, obj):
        return obj.get_product_types_count()
    get_types_count.short_description = 'Product Types'
    
    def get_items_count(self, obj):
        total = sum(pt.get_items_count() for pt in obj.product_types.all())
        return total
    get_items_count.short_description = 'Total Items'

# ============================================================================
# PRODUCT TYPE ADMIN
# ============================================================================

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['type_name', 'product_master', 'is_active', 'display_order', 'get_items_count']
    list_filter = ['product_master', 'is_active']
    search_fields = ['type_name', 'description']
    ordering = ['product_master', 'display_order', 'type_name']
    readonly_fields = ['get_items_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_master', 'type_code', 'type_name', 'description', 'is_active', 'display_order')
        }),
    )
    
    def get_items_count(self, obj):
        return obj.get_items_count()
    get_items_count.short_description = 'Items Count'

# ============================================================================
# PRODUCT ITEM ADMIN
# ============================================================================

@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    list_display = [
        'item_name', 'product_type', 'product_master', 'item_category', 
        'basic_amount', 'total_price', 'is_active', 'display_order'
    ]
    list_filter = [
        'product_type__product_master', 'product_type', 'item_category', 'is_active'
    ]
    search_fields = ['item_name', 'description', 'features']
    ordering = ['product_type', 'display_order', 'item_name']
    readonly_fields = ['total_price', 'get_discount_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_type', 'item_code', 'item_name', 'item_category', 'is_active', 'display_order')
        }),
        ('Description & Features', {
            'fields': ('description', 'features'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('basic_amount', 'cgst', 'sgst', 'total_price', 'old_price', 'get_discount_display'),
            'classes': ('collapse',)
        }),
        ('Token & Installation', {
            'fields': ('token_name', 'token_amount', 'installing_charges'),
            'classes': ('collapse',)
        }),
        ('Special Fields', {
            'fields': ('billing_cycle', 'team_name'),
            'classes': ('collapse',)
        }),
    )
    
    def product_master(self, obj):
        return obj.product_type.product_master.product_name
    product_master.short_description = 'Product Master'
    
    def get_discount_display(self, obj):
        discount = obj.get_discount_percentage()
        if discount > 0:
            return f"{discount}% OFF"
        return "No discount"
    get_discount_display.short_description = 'Discount'

# ============================================================================
# RATE CARD ADMIN
# ============================================================================

@admin.register(RateCardMaster)
class RateCardAdmin(admin.ModelAdmin):
    list_display = ['product_item', 'rate_code', 'rate_date', 'base_amount', 'gst_percent', 'net_amount']
    list_filter = ['rate_date', 'product_item__product_type__product_master']
    search_fields = ['product_item__item_name', 'rate_code']
    ordering = ['-rate_date']
    readonly_fields = ['net_amount']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_item', 'rate_code', 'rate_date')
        }),
        ('Pricing', {
            'fields': ('base_amount', 'gst_percent', 'net_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# ============================================================================
# CUSTOMER ADMIN
# ============================================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'email', 'mobile', 'has_gst', 'state', 'created_at']
    list_filter = ['has_gst', 'state', 'created_at']
    search_fields = ['name', 'company_name', 'email', 'mobile', 'gst_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'company_name', 'email', 'mobile')
        }),
        ('Business Information', {
            'fields': ('has_gst', 'gst_number')
        }),
        ('Address', {
            'fields': ('address', 'state', 'district', 'pincode'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# QUOTE SUBMISSION ADMIN
# ============================================================================

@admin.register(QuoteSubmission)
class QuoteSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'product_item_name', 'product_master', 
        'basic_amount', 'grand_total', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'product_item__product_type__product_master']
    search_fields = ['customer__name', 'customer__email', 'customer__mobile']
    ordering = ['-created_at']
    readonly_fields = ['grand_total', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Product Information', {
            'fields': ('product_item', 'quantity')
        }),
        ('Pricing Details', {
            'fields': ('basic_amount', 'cgst', 'sgst', 'total_amount', 'token_amount', 'installing_charges', 'grand_total'),
            'classes': ('collapse',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return obj.customer.name
    customer_name.short_description = 'Customer'
    
    def product_item_name(self, obj):
        return obj.product_item.item_name
    product_item_name.short_description = 'Product'
    
    def product_master(self, obj):
        return obj.product_item.product_type.product_master.product_name
    product_master.short_description = 'Product Category'

# ============================================================================
# CONTACT SUBMISSION ADMIN
# ============================================================================

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'subject', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# PAYMENT TRANSACTION ADMIN
# ============================================================================

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'amount', 'payment_method', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['customer__name', 'customer__email', 'razorpay_payment_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('customer', 'quote', 'amount', 'payment_method')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_payment_id', 'razorpay_order_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return obj.customer.name
    customer_name.short_description = 'Customer'

# ============================================================================
# PAYMENT SETTINGS ADMIN
# ============================================================================

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ['setting_type', 'title', 'is_active']
    list_filter = ['setting_type', 'is_active']
    search_fields = ['title', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('setting_type', 'title', 'description', 'is_active')
        }),
        ('Razorpay Configuration', {
            'fields': ('razorpay_key_id', 'razorpay_key_secret', 'payment_button_id'),
            'classes': ('collapse',)
        }),
        ('UPI QR Configuration', {
            'fields': ('upi_id', 'qr_image'),
            'classes': ('collapse',)
        }),
        ('Bank Transfer Configuration', {
            'fields': ('account_name', 'account_number', 'ifsc_code', 'bank_name'),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# APPLICANT ADMIN
# ============================================================================

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'reference', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name', 'customer__email', 'reference']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'reference', 'reference_contact')
        }),
        ('Documents', {
            'fields': ('pan_copy', 'aadhar_copy', 'photo', 'gst_certificate', 'authorization_letter', 'company_pan'),
            'classes': ('collapse',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_name(self, obj):
        return obj.customer.name
    customer_name.short_description = 'Customer'

# ============================================================================
# ADMIN SITE CONFIGURATION
# ============================================================================

# Customize admin site
admin.site.site_header = "FusionTec Admin Panel"
admin.site.site_title = "FusionTec Admin"
admin.site.index_title = "Welcome to FusionTec Administration"

# ============================================================================
# SIMPLE PRODUCT TABLES ADMIN (matches requested schema)
# ============================================================================

@admin.register(ProductTypeMaster)
class ProductTypeMasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'prdt_desc', 'sender_email', 'created_at']
    search_fields = ['prdt_desc', 'sender_email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('prdt_desc', 'image')
        }),
        ('Email Configuration', {
            'fields': ('sender_email', 'app_password'),
            'description': 'Email settings for sending notifications for this product type'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductMasterV2)
class ProductMasterV2Admin(admin.ModelAdmin):
    list_display = ['id', 'product_type', 'prdt_desc']
    list_filter = ['product_type']
    search_fields = ['prdt_desc']


@admin.register(ProductSubMaster)
class ProductSubMasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'subprdt_desc']
    list_filter = ['product__product_type', 'product']
    search_fields = ['subprdt_desc', 'product__prdt_desc']


@admin.register(RateCardEntry)
class RateCardEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'sub_product', 'rate_date', 'base_amt', 'gst_percent', 'nett_amt', 'token_amount', 'installation_charge', 't_amount', 'created_at']
    list_filter = ['rate_date', 'sub_product__product__product_type']
    search_fields = ['sub_product__subprdt_desc', 'sub_product__product__prdt_desc', 'token_desc']
    readonly_fields = ['nett_amt', 'cgst', 'sgst', 'token_total', 'token_cgst', 'token_sgst', 'installation_total', 'installation_cgst', 'installation_sgst', 't_amount', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('sub_product', 'rate_date', 'rate_code')
        }),
        ('Base Pricing', {
            'fields': ('base_amt', 'gst_percent', 'nett_amt', 'cgst', 'sgst')
        }),
        ('Token Charges', {
            'fields': ('token_desc', 'token_amount', 'token_gst_percent', 'token_cgst', 'token_sgst', 'token_total')
        }),
        ('Installation Charges', {
            'fields': ('installation_charge', 'installation_gst_percent', 'installation_cgst', 'installation_sgst', 'installation_total')
        }),
        ('Total Amount', {
            'fields': ('t_amount',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ============================================================================
# PRODUCT FORM SUBMISSION ADMIN
# ============================================================================

@admin.register(ProductFormSubmission)
class ProductFormSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'company_name', 'mobile', 'email', 'product_name', 
        'quantity', 'grand_total', 'status', 'created_at'
    ]
    list_filter = ['status', 'has_gst', 'created_at', 'product_id__product_type']
    search_fields = ['customer_name', 'company_name', 'email', 'mobile', 'gst_number']
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'basic_amount', 'cgst_amount', 'sgst_amount', 
        'total_with_gst', 'grand_total'
    ]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'company_name', 'mobile', 'email')
        }),
        ('GST & Address', {
            'fields': ('has_gst', 'gst_number', 'address', 'state', 'district', 'pincode')
        }),
        ('Product & Quantity', {
            'fields': ('product_id', 'quantity')
        }),
        ('Pricing Details', {
            'fields': ('basic_amount', 'cgst_rate', 'sgst_rate', 'cgst_amount', 'sgst_amount', 'total_with_gst')
        }),
        ('Additional Charges', {
            'fields': ('token_amount', 'installation_charges', 'grand_total')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes', 'quote_reference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['convert_to_quote', 'mark_reviewed', 'mark_approved', 'mark_rejected']
    
    def product_name(self, obj):
        return obj.product_id.prdt_desc
    product_name.short_description = 'Product'
    
    def convert_to_quote(self, request, queryset):
        converted_count = 0
        for submission in queryset:
            if submission.status != 'converted':
                try:
                    submission.convert_to_quote()
                    converted_count += 1
                except Exception as e:
                    self.message_user(request, f'Error converting submission #{submission.id}: {str(e)}', level='ERROR')
        
        if converted_count > 0:
            self.message_user(request, f'Successfully converted {converted_count} submission(s) to quote(s).')
    convert_to_quote.short_description = "Convert selected submissions to quotes"
    
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(status='reviewed')
        self.message_user(request, f'{updated} submission(s) marked as reviewed.')
    mark_reviewed.short_description = "Mark as reviewed"
    
    def mark_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} submission(s) marked as approved.')
    mark_approved.short_description = "Mark as approved"
    
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} submission(s) marked as rejected.')
    mark_rejected.short_description = "Mark as rejected"

# ============================================================================
# QUOTE REQUEST ADMIN
# ============================================================================

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'company_name', 'mobile', 'email', 
        'product_type', 'quantity', 'status', 'email_sent', 'created_at'
    ]
    list_filter = ['status', 'email_sent', 'created_at', 'product_type']
    search_fields = ['customer_name', 'company_name', 'email', 'mobile', 'gst_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'email_sent_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'company_name', 'mobile', 'email')
        }),
        ('Product & Quantity', {
            'fields': ('product_type', 'quantity')
        }),
        ('Address Information', {
            'fields': ('address', 'state', 'district', 'pincode'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('gst_number', 'additional_requirements'),
            'classes': ('collapse',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Email Status', {
            'fields': ('email_sent', 'email_sent_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_reviewed', 'mark_quoted', 'mark_accepted', 'mark_rejected', 'mark_closed']
    
    def mark_reviewed(self, request, queryset):
        updated = queryset.update(status='reviewed')
        self.message_user(request, f'{updated} quote request(s) marked as reviewed.')
    mark_reviewed.short_description = "Mark selected as reviewed"
    
    def mark_quoted(self, request, queryset):
        updated = queryset.update(status='quoted')
        self.message_user(request, f'{updated} quote request(s) marked as quoted.')
    mark_quoted.short_description = "Mark selected as quoted"
    
    def mark_accepted(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} quote request(s) marked as accepted.')
    mark_accepted.short_description = "Mark selected as accepted"
    
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} quote request(s) marked as rejected.')
    mark_rejected.short_description = "Mark selected as rejected"
    
    def mark_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f'{updated} quote request(s) marked as closed.')
    mark_closed.short_description = "Mark selected as closed"

# ============================================================================
# DSC MODELS ADMIN
# ============================================================================

@admin.register(DscEnquiry)
class DscEnquiryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'email', 'mobile', 'class_type', 'user_type', 
        'cert_type', 'validity', 'quoted_price', 'created_at'
    ]
    list_filter = ['class_type', 'user_type', 'cert_type', 'validity', 'created_at']
    search_fields = ['name', 'email', 'mobile']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'mobile', 'address')
        }),
        ('DSC Configuration', {
            'fields': ('class_type', 'user_type', 'cert_type', 'validity')
        }),
        ('Options', {
            'fields': ('include_token', 'include_installation', 'outside_india')
        }),
        ('Pricing', {
            'fields': ('quoted_price',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DscSubmission)
class DscSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'email', 'mobile', 'class_type', 'user_type', 
        'cert_type', 'validity', 'quoted_price', 'payment_status', 'status', 'created_at'
    ]
    list_filter = ['class_type', 'user_type', 'cert_type', 'validity', 'payment_status', 'status', 'created_at']
    search_fields = ['name', 'email', 'mobile', 'razorpay_payment_id', 'razorpay_order_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'mobile', 'address', 'company_name', 'gst_number')
        }),
        ('DSC Configuration', {
            'fields': ('class_type', 'user_type', 'cert_type', 'validity')
        }),
        ('Options', {
            'fields': ('include_token', 'include_installation', 'outside_india')
        }),
        ('Pricing', {
            'fields': ('quoted_price',)
        }),
        ('Payment Details', {
            'fields': ('razorpay_payment_id', 'razorpay_order_id', 'payment_status')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_payment_received', 'mark_processing', 'mark_completed', 'mark_cancelled']
    
    def mark_payment_received(self, request, queryset):
        updated = queryset.update(status='payment_received', payment_status='completed')
        self.message_user(request, f'{updated} submission(s) marked as payment received.')
    mark_payment_received.short_description = "Mark as payment received"
    
    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} submission(s) marked as processing.')
    mark_processing.short_description = "Mark as processing"
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} submission(s) marked as completed.')
    mark_completed.short_description = "Mark as completed"
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} submission(s) marked as cancelled.')
    mark_cancelled.short_description = "Mark as cancelled"

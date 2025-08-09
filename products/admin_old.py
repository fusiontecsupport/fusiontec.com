from django.contrib import admin

# contact form submission admin
from .models import ContactSubmission

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'subject', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-submitted_at',)

# ----------------------------------------------------------------------------------------
# Tally section admin
from .models import Tally_1,Tally_Product,Tally_Software_Service, Tally_Upgrade

class Tally_Product_Inline(admin.TabularInline):
    model = Tally_Product
    extra = 1

class Tally_Software_Service_Inline(admin.TabularInline):
    model = Tally_Software_Service
    extra = 1

class Tally_Upgrade_Inline(admin.TabularInline):
    model = Tally_Upgrade
    extra = 1

@admin.register(Tally_1)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('tally_name', 'tally_link')
    inlines = [Tally_Product_Inline,Tally_Software_Service_Inline, Tally_Upgrade_Inline]

from .models import TallyPriceListSubmission

@admin.register(TallyPriceListSubmission)
class TallyPriceListSubmissionAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'mobile', 'product_name', 'product_type', 'total_price', 'created_at')
    search_fields = ('customer_name', 'mobile', 'product_name')
    list_filter = ('product_type', 'created_at')

# ----------------------------------------------------------------------------------------
# e-mudhra section admin

from .models import Emudhra_2, Emudhra_product,EmudhraPriceListSubmission

class EmudhraProductInline(admin.TabularInline):
    model = Emudhra_product
    extra = 1
    fields = ('class_product', 'basic_amount', 'cgst', 'sgst')  # Exclude total_price from here
    readonly_fields = ('total_price',)  # Add this


@admin.register(Emudhra_2)
class Emudhra2Admin(admin.ModelAdmin):
    list_display = ('emudhra_name', 'emudhra_link')
    inlines = [EmudhraProductInline]

@admin.register(EmudhraPriceListSubmission)
class EmudhraPriceListSubmissionAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product_name', 'mobile', 'total_price','created_at')
    search_fields = ('customer_name', 'product_name', 'mobile', 'email')
    list_filter = ('has_gst', 'created_at')

# ----------------------------------------------------------------------------------------
# fusiontec section admin

from .models import Fusiontec_3, Fusiontec_product, Fusiontec_Software, Fusiontec_Service, FusiontecPriceListSubmission

class FusiontecProductInline(admin.TabularInline):
    model = Fusiontec_product
    extra = 1
    fields = ('fusiontec_product',)

class FusiontecSoftwareInline(admin.TabularInline):
    model = Fusiontec_Software
    extra = 1
    fields = ('software_name', 'software_description', 'basic_amount', 'cgst', 'sgst')
    readonly_fields = ('total_price',)

class FusiontecServiceInline(admin.TabularInline):
    model = Fusiontec_Service
    extra = 1
    fields = ('service_name', 'service_description', 'basic_amount', 'cgst', 'sgst')
    readonly_fields = ('total_price',)

@admin.register(Fusiontec_3)
class Fusiontec3Admin(admin.ModelAdmin):
    list_display = ('fusiontec_name', 'fusiontec_link')
    inlines = [FusiontecProductInline, FusiontecSoftwareInline, FusiontecServiceInline]

@admin.register(FusiontecPriceListSubmission)
class PriceListSubmissionAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product_name', 'product_type_detail', 'mobile', 'submitted_at')
    search_fields = ('customer_name', 'mobile', 'email')

# ----------------------------------------------------------------------------------------
# biz section admin

from .models import Biz_4, biz_product, Biz_Service, Biz_Plan, BizPriceListSubmission

class BizProductInline(admin.TabularInline):
    model = biz_product
    extra = 0
    fields = ('team_name', 'old_price', 'new_price', 'cgst', 'sgst', 'billing_cycle')
    readonly_fields = ('total_price',) 

class BizServiceInline(admin.TabularInline):
    model = Biz_Service
    extra = 1
    fields = ('service_name', 'service_description', 'basic_amount', 'cgst', 'sgst', 'billing_cycle')
    readonly_fields = ('total_price',)

class BizPlanInline(admin.TabularInline):
    model = Biz_Plan
    extra = 1
    fields = ('plan_name', 'plan_description', 'old_price', 'new_price', 'cgst', 'sgst', 'billing_cycle')
    readonly_fields = ('total_price',)

@admin.register(Biz_4)
class Biz4Admin(admin.ModelAdmin):
    list_display = ('biz_name', 'biz_link')
    inlines = [BizProductInline, BizServiceInline, BizPlanInline]


@admin.register(BizPriceListSubmission)
class BizPriceListSubmissionAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product_name', 'business_plan_name', 'total_price', 'created_at')
    list_filter = ('created_at', 'business_plan_name')
    search_fields = ('customer_name', 'product_name', 'business_plan_name')

# ----------------------------------------------------------------------------------------
# razorpay admin for form

from .models import RazorpayTransactionForm

@admin.register(RazorpayTransactionForm)
class RazorpayTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer_name','product_name','razorpay_payment_id','razorpay_order_id','amount','status','created_at',)
    search_fields = ('customer_name', 'razorpay_payment_id', 'razorpay_order_id')
    list_filter = ('status', 'created_at')


#----------------------------------------------------------------
# netbanking section for razorpay button
# Note: RazorpayInfo is now managed through custom admin views
# from .models import RazorpayInfo

# @admin.register(RazorpayInfo)
# class RazorpayInfoAdmin(admin.ModelAdmin):
#     list_display = ['title', 'payment_button_id']

#----------------------------------------------------------------
# netbanking section for QR editing section
# Note: CompanyPaymentInfoQR is now managed through custom admin views
# from .models import CompanyPaymentInfoQR

# @admin.register(CompanyPaymentInfoQR)
# class CompanyPaymentInfoQRAdmin(admin.ModelAdmin):
#     list_display = ['company_name', 'upi_id']
#     search_fields = ['company_name', 'upi_id']

#----------------------------------------------------------------
# netbanking section for Banking details
# Note: BankTransferInfo is now managed through custom admin views
# from .models import BankTransferInfo

# @admin.register(BankTransferInfo)
# class BankTransferInfoAdmin(admin.ModelAdmin):
#     list_display = ['account_name', 'account_number', 'ifsc_code', 'bank_name']
#     search_fields = ['account_name', 'bank_name', 'ifsc_code']


from .models import Applicant
@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile_number', 'email', 'reference', 'reference_contact', 'submitted_at']
    search_fields = ['name', 'mobile_number', 'email', 'reference']
    list_filter = ['submitted_at']
    readonly_fields = ['submitted_at']

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

# ----------------------------------------------------------------------------------------

# e-mudhra section admin

from .models import Emudhra_2, Emudhra_product

class EmudhraProductInline(admin.TabularInline):
    model = Emudhra_product
    extra = 1
    fields = ('class_product', 'emudhra_rate')

@admin.register(Emudhra_2)
class Emudhra2Admin(admin.ModelAdmin):
    list_display = ('emudhra_name', 'emudhra_link')
    inlines = [EmudhraProductInline]

# ----------------------------------------------------------------------------------------

# fusiontec section admin

from .models import Fusiontec_3, Fusiontec_product

class FusiontecProductInline(admin.TabularInline):
    model = Fusiontec_product
    extra = 1
    fields = ('fusiontec_product',)

@admin.register(Fusiontec_3)
class Fusiontec3Admin(admin.ModelAdmin):
    list_display = ('fusiontec_name', 'fusiontec_link')
    inlines = [FusiontecProductInline]

# ----------------------------------------------------------------------------------------

# biz section admin

from django.contrib import admin
from .models import Biz_4, biz_product

class BizProductInline(admin.TabularInline):
    model = biz_product
    extra = 1
    fields = ('team_name', 'old_price', 'new_price', 'billing_cycle')

@admin.register(Biz_4)
class Biz4Admin(admin.ModelAdmin):
    list_display = ('biz_name', 'biz_link')
    inlines = [BizProductInline]

# ----------------------------------------------------------------------------------------


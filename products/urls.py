from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ============================================================================
    # MAIN PAGES
    # ============================================================================
    path('', views.index, name='index'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product-type/<int:type_id>/', views.product_type_products, name='product_type_products'),
    
    # ============================================================================
    # QUOTE & CONTACT FORMS
    # ============================================================================
    path('quote/<int:product_id>/', views.quote_form, name='quote_form'),
    path('quote-detail/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('contact/', views.contact_form, name='contact_form'),
    
    # ============================================================================
    # API ENDPOINTS
    # ============================================================================
    path('api/states/', views.get_states, name='get_states'),
    path('api/districts/<str:state>/', views.get_districts, name='get_districts'),
    
    # ============================================================================
    # CUSTOM ADMIN PANEL URLs
    # ============================================================================
    path('admin-login/', views.custom_admin_login, name='custom_admin_login'),
    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/dashboard/data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('admin-contacts/', views.custom_admin_contacts, name='custom_admin_contacts'),
    path('admin-quotes/', views.custom_admin_quotes, name='custom_admin_quotes'),
    path('admin-products/', views.custom_admin_products, name='custom_admin_products'),
    path('admin-tally-submissions/', views.custom_admin_tally_submissions, name='custom_admin_tally_submissions'),
    path('admin-emudhra-submissions/', views.custom_admin_emudhra_submissions, name='custom_admin_emudhra_submissions'),
    path('admin-fusiontec-submissions/', views.custom_admin_fusiontec_submissions, name='custom_admin_fusiontec_submissions'),
    path('admin-biz-submissions/', views.custom_admin_biz_submissions, name='custom_admin_biz_submissions'),
    path('admin-payments/', views.custom_admin_payments, name='custom_admin_payments'),
    path('admin-applicants/', views.custom_admin_applicants, name='custom_admin_applicants'),
    path('admin-settings/', views.custom_admin_settings, name='custom_admin_settings'),
    
    # legacy routes kept but redirected inside views
    path('admin-product-types/<int:master_id>/', views.admin_product_types, name='admin_product_types'),
    path('admin-product-items/<int:type_id>/', views.admin_product_items, name='admin_product_items'),
    # Use ProductMasterV2 id for rate cards
    path('admin-rate-cards/<int:item_id>/', views.admin_rate_cards, name='admin_rate_cards'),
    path('admin-logout/', views.custom_admin_logout, name='custom_admin_logout'),
    
    # ============================================================================
    # PRODUCT MANAGEMENT URLs (New Structure)
    # ============================================================================
    path('admin-add-fusiontec-product/', views.add_fusiontec_product, name='add_fusiontec_product'),
    path('admin-edit-fusiontec-product/<int:product_id>/', views.edit_fusiontec_product, name='edit_fusiontec_product'),
    path('admin-add-biz-product/', views.add_biz_product, name='add_biz_product'),
    path('admin-edit-biz-product/<int:product_id>/', views.edit_biz_product, name='edit_biz_product'),
    path('admin-add-emudhra-product/', views.add_emudhra_product, name='add_emudhra_product'),
    path('admin-edit-emudhra-product/<int:product_id>/', views.edit_emudhra_product, name='edit_emudhra_product'),
    path('admin-add-tally-product/', views.add_tally_product, name='add_tally_product'),
    path('admin-edit-tally-product/<int:product_id>/', views.edit_tally_product, name='edit_tally_product'),
    
    # ============================================================================
    # SETTINGS MANAGEMENT URLs
    # ============================================================================
    path('admin-edit-razorpay-info/<int:info_id>/', views.edit_razorpay_info, name='edit_razorpay_info'),
    path('admin-add-razorpay-info/', views.add_razorpay_info, name='add_razorpay_info'),
    path('admin-edit-qr-info/<int:info_id>/', views.edit_qr_info, name='edit_qr_info'),
    path('admin-add-qr-info/', views.add_qr_info, name='add_qr_info'),
    path('admin-edit-bank-info/<int:info_id>/', views.edit_bank_info, name='edit_bank_info'),
    path('admin-add-bank-info/', views.add_bank_info, name='add_bank_info'),
]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

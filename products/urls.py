from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ============================================================================
    # MAIN PAGES
    # ============================================================================
    path('', views.index, name='index'),
    path('home/', views.index, name='home'),
    path('about/', views.about_page, name='about'),
    path('process/', views.process_page, name='process'),
    path('products/', views.products_page, name='products'),
    path('contact/', views.contact_page, name='contact'),
    path('dsc/', views.dsc_page, name='dsc'),
    path('net_banking/', views.net_banking_page, name='net_banking'),
    path('catalog/', views.product_catalog, name='product_catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product-type/<int:type_id>/', views.product_type_products, name='product_type_products'),
    path('product-form/<int:type_id>/', views.product_type_form, name='product_type_form'),
    path('save-product-submission/', views.save_product_submission, name='save_product_submission'),
    path('api/payments/create-order/', views.create_payment_order, name='create_payment_order'),
    path('api/payments/verify/', views.verify_payment, name='verify_payment'),
    path('submit-quote/', views.submit_quote, name='submit_quote'),
    # DSC form (e-Mudhra-like)
    path('digital_signature/', views.dsc_form, name='dsc_form'),
    path('dsc/price-list/', views.dsc_price_list_page, name='dsc_price_list_page'),
    path('dsc/submit/', views.dsc_integrated_submission, name='dsc_integrated_submission'),

    path('api/dsc-price/', views.dsc_price_api, name='dsc_price_api'),
    path('api/dsc-options/', views.dsc_options_api, name='dsc_options_api'),
    path('api/dsc-enquiry/', views.dsc_enquiry_api, name='dsc_enquiry_api'),
    path('api/dsc-submission/', views.dsc_submission_api, name='dsc_submission_api'),
    path('api/dsc-payment/create-order/', views.create_dsc_payment_order, name='create_dsc_payment_order'),
    path('api/dsc-payment/test/', views.test_dsc_payment_api, name='test_dsc_payment_api'),
    path('api/dsc-payment/verify/', views.verify_dsc_payment, name='verify_dsc_payment'),
    path('api/dsc-documents/', views.dsc_documents_upload_api, name='dsc_documents_upload_api'),
    path('api/dsc-download-pdf/', views.dsc_download_pdf_api, name='dsc_download_pdf_api'),
    
    # ============================================================================
    # QUOTE & CONTACT FORMS
    # ============================================================================
    path('quote/<int:product_id>/', views.quote_form, name='quote_form'),
    path('quote-detail/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('contact/', views.contact_form, name='contact_form'),
    path('footer-contact/', views.footer_contact_form, name='footer_contact_form'),
    
    # ============================================================================
    # API ENDPOINTS
    # ============================================================================
    path('api/test/', views.test_api, name='test_api'),
    path('api/states/', views.get_states, name='get_states'),
    path('api/districts/<str:state>/', views.get_districts, name='get_districts'),
    path('api/submission/<int:submission_id>/', views.get_submission_details, name='get_submission_details'),
    path('api/submission/<int:submission_id>/convert/', views.convert_submission_to_quote, name='convert_submission_to_quote'),
    
    # ============================================================================
    # CUSTOM ADMIN PANEL URLs
    # ============================================================================
    path('admin-login/', views.custom_admin_login, name='custom_admin_login'),
    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/dashboard/data/', views.dashboard_data_api, name='dashboard_data_api'),
    path('admin-contacts/', views.custom_admin_contacts, name='custom_admin_contacts'),
    path('admin-dsc-enquiries/', views.custom_admin_dsc_enquiries, name='custom_admin_dsc_enquiries'),
    path('admin-dsc-submissions/', views.custom_admin_dsc_submissions, name='custom_admin_dsc_submissions'),
    path('admin-quotes/', views.custom_admin_quotes, name='custom_admin_quotes'),
    path('admin-form-submissions/', views.custom_admin_form_submissions, name='custom_admin_form_submissions'),
    path('admin-quote-requests/', views.custom_admin_quote_requests, name='custom_admin_quote_requests'),
    path('api/quote-request/<int:request_id>/', views.quote_request_detail, name='quote_request_detail'),
    path('api/quote-request/<int:request_id>/update-status/', views.update_quote_request_status, name='update_quote_request_status'),
    path('admin-products/', views.custom_admin_products, name='custom_admin_products'),
    path('admin-dsc-prices/', views.admin_dsc_prices, name='admin_dsc_prices'),
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

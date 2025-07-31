from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('tally_form/', views.tally_form, name='tally_form'),
    path('emudhra_form/', views.emudhra_form, name='emudhra_form'),
    path('fusiontec_form/', views.fusiontec_form, name='fusiontec_form'),
    path('biz_form/', views.biz_form, name='biz_form'),

    path('save-tally-form/', views.save_tally_form, name='save_tally_form'),                                #for tally form
    path('fetch-tally-details/', views.fetch_tally_details, name='fetch_tally_details'),                     

    # form saving path
    path('save-price-list/', views.save_price_list_submission, name='save_price_list'),                      #for e-mudhra
    path('fusiontec_price_list_form/', views.fusiontec_price_list_form, name='fusiontec_price_list_form'),   #for fusiontec
    path('save-pi/', views.save_pi_data, name='save_pi_data'),                                               #for biz

    #link for dynamic dropdown
    path('api/states/', views.get_states, name='get_states'),
    path('api/districts/<str:state>/', views.get_districts, name='get_districts'),

    #razor pay in form
    path("verify-razorpay-payment/", views.razorpay_verify, name="razorpay_verify"),
    path("create_order/", views.create_order, name="create_order"),

    path("dsc_form/", views.dsctypeform, name="dsc_form"),

    # ============================================================================
    # CUSTOM ADMIN PANEL URLs (Without Django Admin)
    # ============================================================================
    path('admin/', views.custom_admin_login, name='old_admin_redirect'),  # Redirect old admin URL
    path('admin-panel/', views.custom_admin_login, name='admin_panel_redirect'),  # Redirect for common URL
    path('admin-login/', views.custom_admin_login, name='custom_admin_login'),
    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin-contacts/', views.custom_admin_contacts, name='custom_admin_contacts'),
    path('admin-tally/', views.custom_admin_tally_submissions, name='custom_admin_tally_submissions'),
    path('admin-emudhra/', views.custom_admin_emudhra_submissions, name='custom_admin_emudhra_submissions'),
    path('admin-fusiontec/', views.custom_admin_fusiontec_submissions, name='custom_admin_fusiontec_submissions'),
    path('admin-biz/', views.custom_admin_biz_submissions, name='custom_admin_biz_submissions'),
    path('admin-payments/', views.custom_admin_payments, name='custom_admin_payments'),
    path('admin-applicants/', views.custom_admin_applicants, name='custom_admin_applicants'),
    path('admin-products/', views.custom_admin_products, name='custom_admin_products'),
    path('admin-settings/', views.custom_admin_settings, name='custom_admin_settings'),
    
    # Custom Edit URLs for Products
    path('admin-products/tally/<int:product_id>/edit/', views.edit_tally_product, name='edit_tally_product'),
    path('admin-products/emudhra/<int:product_id>/edit/', views.edit_emudhra_product, name='edit_emudhra_product'),
    path('admin-products/fusiontec/<int:product_id>/edit/', views.edit_fusiontec_product, name='edit_fusiontec_product'),
    path('admin-products/biz/<int:product_id>/edit/', views.edit_biz_product, name='edit_biz_product'),
    
    # Custom Add URLs for Products
    path('admin-products/tally/add/', views.add_tally_product, name='add_tally_product'),
    path('admin-products/emudhra/add/', views.add_emudhra_product, name='add_emudhra_product'),
    path('admin-products/fusiontec/add/', views.add_fusiontec_product, name='add_fusiontec_product'),
    path('admin-products/biz/add/', views.add_biz_product, name='add_biz_product'),
    
    # Custom RazorpayInfo URLs
    path('admin-settings/razorpay/<int:info_id>/edit/', views.edit_razorpay_info, name='edit_razorpay_info'),
    path('admin-settings/razorpay/add/', views.add_razorpay_info, name='add_razorpay_info'),
    
    # Custom CompanyPaymentInfoQR URLs
    path('admin-settings/qr/<int:info_id>/edit/', views.edit_qr_info, name='edit_qr_info'),
    path('admin-settings/qr/add/', views.add_qr_info, name='add_qr_info'),
    
    # Custom BankTransferInfo URLs
    path('admin-settings/bank/<int:info_id>/edit/', views.edit_bank_info, name='edit_bank_info'),
    path('admin-settings/bank/add/', views.add_bank_info, name='add_bank_info'),
    
    # Custom Tally Related Items Management URLs
    path('admin-products/tally/<int:product_id>/products/', views.manage_tally_products, name='manage_tally_products'),
    path('admin-products/tally/<int:product_id>/services/', views.manage_tally_services, name='manage_tally_services'),
    path('admin-products/tally/<int:product_id>/upgrades/', views.manage_tally_upgrades, name='manage_tally_upgrades'),
    path('admin-products/tally/delete/<int:item_id>/<str:item_type>/', views.delete_tally_product_item, name='delete_tally_product_item'),
    
    # Unified Product Management URLs
    path('admin-products/<str:product_type>/<int:product_id>/manage/', views.manage_product_items, name='manage_product_items'),
    path('admin-products/<str:product_type>/edit/<int:item_id>/<str:item_type>/', views.edit_product_item, name='edit_product_item'),
    path('admin-products/<str:product_type>/delete/<int:item_id>/<str:item_type>/', views.delete_product_item, name='delete_product_item'),
]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

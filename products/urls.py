from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    # path('tally_form/', views.tally_form, name='tally_form'),
    path('emudhra_form/', views.emudhra_form, name='emudhra_form'),
    path('fusiontec_form/', views.fusiontec_form, name='fusiontec_form'),
    path('biz_form/', views.biz_form, name='biz_form'),

    path('tally_form/', views.tally_form, name='tally_form'),
    path('save-tally-form/', views.save_tally_form, name='save_tally_form'),
    path('fetch-tally-details/', views.fetch_tally_details, name='fetch_tally_details'),        #for tally form


    # form saving path
    path('save-price-list/', views.save_price_list_submission, name='save_price_list'),     #for e-mudhra
    path('fusiontec_price_list_form/', views.fusiontec_price_list_form, name='fusiontec_price_list_form'),     #for fusiontec
    path('save-pi/', views.save_pi_data, name='save_pi_data'),   #for fusiontec form
    # path('fetch-tally-details/', views.fetch_tally_details, name='fetch_tally_details'),        #for tally form


]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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


]

# Serve static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusiontec.settings')
django.setup()

from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from products.models import ProductTypeMaster

def test_email_credentials():
    """Test email credentials for ProductTypeMaster entries"""
    
    # Get all product types with email credentials
    product_types = ProductTypeMaster.objects.filter(
        sender_email__isnull=False,
        app_password__isnull=False
    ).exclude(sender_email='', app_password='')
    
    print(f"Found {product_types.count()} product types with email credentials:")
    
    for pt in product_types:
        print(f"\nTesting: {pt.prdt_desc}")
        print(f"Email: {pt.sender_email}")
        print(f"Password configured: {'Yes' if pt.app_password else 'No'}")
        
        try:
            # Configure email backend
            email_backend = EmailBackend(
                host='smtp.gmail.com',
                port=587,
                username=pt.sender_email,
                password=pt.app_password,
                use_tls=True,
                fail_silently=False
            )
            
            # Test email
            test_email = EmailMessage(
                subject='Test Email from FusionTec Quote System',
                body=f'This is a test email from the FusionTec quote system for product type: {pt.prdt_desc}',
                from_email=pt.sender_email,
                to=[pt.sender_email],  # Send to self for testing
            )
            test_email.connection = email_backend
            test_email.send()
            
            print("✅ Email sent successfully!")
            
        except Exception as e:
            print(f"❌ Email failed: {str(e)}")
            print(f"   Error type: {type(e).__name__}")

if __name__ == '__main__':
    test_email_credentials()

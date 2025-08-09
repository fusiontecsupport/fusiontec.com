#!/usr/bin/env python
"""
Database Initialization Script for FusionTec
This script will create the initial product structure and sample data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fusiontec.settings')
django.setup()

from products.models import ProductMaster, ProductType, ProductItem

def create_initial_structure():
    """Create the initial product structure"""
    
    print("🚀 Creating FusionTec Database Structure...")
    
    # ============================================================================
    # CREATE PRODUCT MASTERS
    # ============================================================================
    
    print("\n📦 Creating Product Masters...")
    
    # Tally Software
    tally_master, created = ProductMaster.objects.get_or_create(
        product_code='tally',
        defaults={
            'product_name': 'Tally Software',
            'description': 'Leading accounting and business management software for businesses of all sizes',
            'display_order': 1
        }
    )
    if created:
        print("✅ Created Tally Software master")
    else:
        print("ℹ️  Tally Software master already exists")
    
    # E-Mudhra
    emudhra_master, created = ProductMaster.objects.get_or_create(
        product_code='emudhra',
        defaults={
            'product_name': 'E-Mudhra',
            'description': 'Digital signature and certificate solutions for secure online transactions',
            'display_order': 2
        }
    )
    if created:
        print("✅ Created E-Mudhra master")
    else:
        print("ℹ️  E-Mudhra master already exists")
    
    # FusionTec Software
    fusiontec_master, created = ProductMaster.objects.get_or_create(
        product_code='fusiontec',
        defaults={
            'product_name': 'FusionTec Software',
            'description': 'Custom software solutions tailored to your business needs',
            'display_order': 3
        }
    )
    if created:
        print("✅ Created FusionTec Software master")
    else:
        print("ℹ️  FusionTec Software master already exists")
    
    # Business Intelligence
    biz_master, created = ProductMaster.objects.get_or_create(
        product_code='biz',
        defaults={
            'product_name': 'Business Intelligence',
            'description': 'Advanced analytics and business intelligence solutions',
            'display_order': 4
        }
    )
    if created:
        print("✅ Created Business Intelligence master")
    else:
        print("ℹ️  Business Intelligence master already exists")
    
    # ============================================================================
    # CREATE PRODUCT TYPES
    # ============================================================================
    
    print("\n🏷️  Creating Product Types...")
    
    # Tally Types
    tally_types = {}
    tally_type_data = [
        ('main', 'Main Products', 'Core Tally software products'),
        ('services', 'Services', 'Tally software services and support'),
        ('upgrades', 'Upgrades', 'Tally software upgrades and versions')
    ]
    
    for type_code, type_name, description in tally_type_data:
        product_type, created = ProductType.objects.get_or_create(
            product_master=tally_master,
            type_code=type_code,
            defaults={
                'type_name': type_name,
                'description': description,
                'display_order': len(tally_types) + 1
            }
        )
        tally_types[type_code] = product_type
        if created:
            print(f"✅ Created Tally {type_name}")
        else:
            print(f"ℹ️  Tally {type_name} already exists")
    
    # E-Mudhra Types
    emudhra_main_type, created = ProductType.objects.get_or_create(
        product_master=emudhra_master,
        type_code='main',
        defaults={
            'type_name': 'Main Products',
            'description': 'Core E-Mudhra digital signature products',
            'display_order': 1
        }
    )
    if created:
        print("✅ Created E-Mudhra Main Products type")
    else:
        print("ℹ️  E-Mudhra Main Products type already exists")
    
    # FusionTec Types
    fusiontec_types = {}
    fusiontec_type_data = [
        ('main', 'Main Products', 'Core FusionTec software products'),
        ('software', 'Software Solutions', 'Custom software development'),
        ('services', 'Services', 'Software consulting and support services')
    ]
    
    for type_code, type_name, description in fusiontec_type_data:
        product_type, created = ProductType.objects.get_or_create(
            product_master=fusiontec_master,
            type_code=type_code,
            defaults={
                'type_name': type_name,
                'description': description,
                'display_order': len(fusiontec_types) + 1
            }
        )
        fusiontec_types[type_code] = product_type
        if created:
            print(f"✅ Created FusionTec {type_name}")
        else:
            print(f"ℹ️  FusionTec {type_name} already exists")
    
    # Business Intelligence Types
    bi_types = {}
    bi_type_data = [
        ('main', 'Main Products', 'Core BI and analytics products'),
        ('services', 'Services', 'BI consulting and implementation services'),
        ('plans', 'Subscription Plans', 'Flexible subscription-based BI solutions')
    ]
    
    for type_code, type_name, description in bi_type_data:
        product_type, created = ProductType.objects.get_or_create(
            product_master=biz_master,
            type_code=type_code,
            defaults={
                'type_name': type_name,
                'description': description,
                'display_order': len(bi_types) + 1
            }
        )
        bi_types[type_code] = product_type
        if created:
            print(f"✅ Created Business Intelligence {type_name}")
        else:
            print(f"ℹ️  Business Intelligence {type_name} already exists")
    
    # ============================================================================
    # CREATE SAMPLE PRODUCT ITEMS
    # ============================================================================
    
    print("\n🛍️  Creating Sample Product Items...")
    
    # Tally Sample Items
    tally_items = [
        {
            'type': tally_types['main'],
            'code': 'tally_prime',
            'name': 'Tally Prime',
            'category': 'product',
            'basic_amount': 18000.00,
            'cgst': 1620.00,
            'sgst': 1620.00,
            'description': 'Complete business management solution',
            'features': 'Accounting, Inventory, GST, Banking, Payroll'
        },
        {
            'type': tally_types['services'],
            'code': 'tally_support',
            'name': 'Tally Support',
            'category': 'service',
            'basic_amount': 5000.00,
            'cgst': 450.00,
            'sgst': 450.00,
            'description': 'Professional Tally support and training',
            'features': 'Remote support, On-site training, Data recovery'
        }
    ]
    
    for item_data in tally_items:
        product_item, created = ProductItem.objects.get_or_create(
            product_type=item_data['type'],
            item_code=item_data['code'],
            defaults={
                'item_name': item_data['name'],
                'item_category': item_data['category'],
                'basic_amount': item_data['basic_amount'],
                'cgst': item_data['cgst'],
                'sgst': item_data['sgst'],
                'description': item_data['description'],
                'features': item_data['features'],
                'display_order': 1
            }
        )
        if created:
            print(f"✅ Created Tally item: {item_data['name']}")
        else:
            print(f"ℹ️  Tally item already exists: {item_data['name']}")
    
    # E-Mudhra Sample Items
    emudhra_items = [
        {
            'type': emudhra_main_type,
            'code': 'emudhra_class2',
            'name': 'E-Mudhra Class 2 Certificate',
            'category': 'product',
            'basic_amount': 1500.00,
            'cgst': 135.00,
            'sgst': 135.00,
            'description': 'Digital signature certificate for individuals',
            'features': 'Secure digital signatures, Document authentication, Legal validity'
        }
    ]
    
    for item_data in emudhra_items:
        product_item, created = ProductItem.objects.get_or_create(
            product_type=item_data['type'],
            item_code=item_data['code'],
            defaults={
                'item_name': item_data['name'],
                'item_category': item_data['category'],
                'basic_amount': item_data['basic_amount'],
                'cgst': item_data['cgst'],
                'sgst': item_data['sgst'],
                'description': item_data['description'],
                'features': item_data['features'],
                'display_order': 1
            }
        )
        if created:
            print(f"✅ Created E-Mudhra item: {item_data['name']}")
        else:
            print(f"ℹ️  E-Mudhra item already exists: {item_data['name']}")
    
    # FusionTec Sample Items
    fusiontec_items = [
        {
            'type': fusiontec_types['software'],
            'code': 'fusiontec_crm',
            'name': 'FusionTec CRM',
            'category': 'product',
            'basic_amount': 25000.00,
            'cgst': 2250.00,
            'sgst': 2250.00,
            'description': 'Custom CRM solution for business growth',
            'features': 'Lead management, Sales tracking, Customer analytics, Mobile app'
        }
    ]
    
    for item_data in fusiontec_items:
        product_item, created = ProductItem.objects.get_or_create(
            product_type=item_data['type'],
            item_code=item_data['code'],
            defaults={
                'item_name': item_data['name'],
                'item_category': item_data['category'],
                'basic_amount': item_data['basic_amount'],
                'cgst': item_data['cgst'],
                'sgst': item_data['sgst'],
                'description': item_data['description'],
                'features': item_data['features'],
                'display_order': 1
            }
        )
        if created:
            print(f"✅ Created FusionTec item: {item_data['name']}")
        else:
            print(f"ℹ️  FusionTec item already exists: {item_data['name']}")
    
    # Business Intelligence Sample Items
    bi_items = [
        {
            'type': bi_types['plans'],
            'code': 'bi_basic',
            'name': 'BI Basic Plan',
            'category': 'plan',
            'basic_amount': 5000.00,
            'cgst': 450.00,
            'sgst': 450.00,
            'description': 'Basic business intelligence subscription',
            'features': 'Monthly reports, Basic analytics, Email support',
            'billing_cycle': 'Billed Monthly | Per User'
        }
    ]
    
    for item_data in bi_items:
        product_item, created = ProductItem.objects.get_or_create(
            product_type=item_data['type'],
            item_code=item_data['code'],
            defaults={
                'item_name': item_data['name'],
                'item_category': item_data['category'],
                'basic_amount': item_data['basic_amount'],
                'cgst': item_data['cgst'],
                'sgst': item_data['sgst'],
                'description': item_data['description'],
                'features': item_data['features'],
                'billing_cycle': item_data.get('billing_cycle', 'Billed for 1 Year | Per Device'),
                'display_order': 1
            }
        )
        if created:
            print(f"✅ Created BI item: {item_data['name']}")
        else:
            print(f"ℹ️  BI item already exists: {item_data['name']}")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    
    print("\n" + "="*60)
    print("🎉 DATABASE INITIALIZATION COMPLETED!")
    print("="*60)
    
    # Count totals
    total_masters = ProductMaster.objects.count()
    total_types = ProductType.objects.count()
    total_items = ProductItem.objects.count()
    
    print(f"\n📊 Database Summary:")
    print(f"   • Product Masters: {total_masters}")
    print(f"   • Product Types: {total_types}")
    print(f"   • Product Items: {total_items}")
    
    print(f"\n🔗 Structure Created:")
    print(f"   • Tally Software → {tally_master.product_types.count()} types → {sum(t.get_items_count() for t in tally_master.product_types.all())} items")
    print(f"   • E-Mudhra → {emudhra_master.product_types.count()} types → {sum(t.get_items_count() for t in emudhra_master.product_types.all())} items")
    print(f"   • FusionTec Software → {fusiontec_master.product_types.count()} types → {sum(t.get_items_count() for t in fusiontec_master.product_types.all())} items")
    print(f"   • Business Intelligence → {biz_master.product_types.count()} types → {sum(t.get_items_count() for t in biz_master.product_types.all())} items")
    
    print(f"\n✨ Next Steps:")
    print(f"   1. Access Django admin at /admin/")
    print(f"   2. Review and customize the created structure")
    print(f"   3. Add more products, types, and items as needed")
    print(f"   4. Update your views and templates to use new models")
    
    print(f"\n🚀 Your FusionTec database is ready to use!")

if __name__ == "__main__":
    try:
        create_initial_structure()
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        print("Please check your Django setup and try again.")
        sys.exit(1)

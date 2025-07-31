from django.core.management.base import BaseCommand
from decimal import Decimal, InvalidOperation
from products.models import (
    Tally_Product, Tally_Software_Service, Tally_Upgrade,
    Emudhra_product, EmudhraPriceListSubmission,
    Fusiontec_Software, Fusiontec_Service,
    biz_product, Biz_Service, Biz_Plan,
    BizPriceListSubmission, TallyPriceListSubmission
)

class Command(BaseCommand):
    help = 'Fix invalid Decimal field data in the database'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fix Decimal fields...')
        
        # List of models with Decimal fields
        models_with_decimals = [
            (Tally_Product, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (Tally_Software_Service, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (Tally_Upgrade, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (Emudhra_product, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (EmudhraPriceListSubmission, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (Fusiontec_Software, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (Fusiontec_Service, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (biz_product, ['old_price', 'new_price', 'cgst', 'sgst', 'total_price']),
            (Biz_Service, ['basic_amount', 'cgst', 'sgst', 'total_price']),
            (Biz_Plan, ['old_price', 'new_price', 'cgst', 'sgst', 'total_price']),
            (BizPriceListSubmission, ['original_price', 'new_price', 'cgst', 'sgst', 'total_price']),
            (TallyPriceListSubmission, ['basic_amount', 'cgst', 'sgst', 'total_price']),
        ]
        
        total_fixed = 0
        
        for model, decimal_fields in models_with_decimals:
            self.stdout.write(f'Checking {model.__name__}...')
            
            try:
                # Get all objects for this model
                objects = model.objects.all()
                fixed_count = 0
                
                for obj in objects:
                    needs_save = False
                    
                    for field_name in decimal_fields:
                        field_value = getattr(obj, field_name)
                        
                        # Check if the field value is invalid
                        if field_value is not None:
                            try:
                                # Try to convert to Decimal to see if it's valid
                                Decimal(str(field_value))
                            except (InvalidOperation, ValueError, TypeError):
                                # Invalid value, set to 0
                                setattr(obj, field_name, Decimal('0'))
                                needs_save = True
                                self.stdout.write(f'  Fixed {field_name} in {model.__name__} ID {obj.id}')
                    
                    if needs_save:
                        obj.save()
                        fixed_count += 1
                
                total_fixed += fixed_count
                self.stdout.write(f'  Fixed {fixed_count} objects in {model.__name__}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {model.__name__}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Completed! Fixed {total_fixed} objects total.')) 
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import ProductMasterV2, ProductSubMaster, RateCardEntry


class Command(BaseCommand):
    help = (
        "Create a default ProductSubMaster for each ProductMaster referenced by RateCardEntry "
        "and attach existing RateCardEntry rows to that sub product."
    )

    def handle(self, *args, **options):
        updated = 0
        created_subs = 0
        with transaction.atomic():
            # For each rate card with legacy product but no sub_product
            for rc in RateCardEntry.objects.select_related('product', 'sub_product').all():
                if rc.sub_product is None and rc.product is not None:
                    # Get or create a default sub product under this product
                    sub, created = ProductSubMaster.objects.get_or_create(
                        product=rc.product,
                        subprdt_desc='Default',
                    )
                    if created:
                        created_subs += 1
                    rc.sub_product = sub
                    rc.save(update_fields=['sub_product'])
                    updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Linked {updated} RateCardEntry rows to sub products. Created {created_subs} new sub products."
        ))




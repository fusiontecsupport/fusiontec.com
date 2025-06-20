# Generated by Django 5.1.8 on 2025-06-18 09:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_razorpaytransactionform_product_detail_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='razorpaytransactionform',
            name='product_detail',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='razorpaytransactionform',
            name='product_name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='razorpaytransactionform',
            name='product_type',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]

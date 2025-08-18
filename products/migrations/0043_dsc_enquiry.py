from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('products', '0042_alter_customer_email_alter_customer_mobile'),
	]

	operations = [
		migrations.CreateModel(
			name='DscEnquiry',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('name', models.CharField(max_length=255)),
				('email', models.EmailField(max_length=255)),
				('mobile', models.CharField(max_length=20)),
				('address', models.TextField(blank=True, null=True)),
				('class_type', models.CharField(max_length=20)),
				('user_type', models.CharField(max_length=20)),
				('cert_type', models.CharField(max_length=20)),
				('validity', models.CharField(max_length=5)),
				('include_token', models.BooleanField(default=False)),
				('include_installation', models.BooleanField(default=False)),
				('outside_india', models.BooleanField(default=False)),
				('quoted_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
			],
			options={
				'ordering': ['-created_at'],
				'verbose_name': 'DSC Enquiry',
				'verbose_name_plural': 'DSC Enquiries',
			},
		),
	]



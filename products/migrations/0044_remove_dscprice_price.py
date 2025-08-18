from django.db import migrations


def drop_price_column(apps, schema_editor):
	with schema_editor.connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT COUNT(*) FROM information_schema.COLUMNS
			WHERE TABLE_SCHEMA = DATABASE()
			  AND TABLE_NAME = 'products_dscprice'
			  AND COLUMN_NAME = 'price'
			"""
		)
		count = cursor.fetchone()[0]
		if count and int(count) > 0:
			cursor.execute("ALTER TABLE products_dscprice DROP COLUMN price")


class Migration(migrations.Migration):

	dependencies = [
		('products', '0043_dsc_enquiry'),
	]

	operations = [
		migrations.RunPython(drop_price_column, reverse_code=migrations.RunPython.noop),
	]

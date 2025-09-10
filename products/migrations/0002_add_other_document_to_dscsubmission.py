from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dscsubmission',
            name='other_document',
            field=models.FileField(blank=True, null=True, upload_to='uploads/other/'),
        ),
    ]

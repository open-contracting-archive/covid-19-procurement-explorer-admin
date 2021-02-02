# Generated by Django 3.1.2 on 2021-02-01 10:49

import content.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0036_auto_20210201_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataimport',
            name='import_file',
            field=models.FileField(null=True, upload_to='documents/%Y/%m/%d', validators=[content.validators.validate_file_extension]),
        ),
    ]
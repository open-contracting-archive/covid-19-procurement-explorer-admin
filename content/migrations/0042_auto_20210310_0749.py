# Generated by Django 3.1.2 on 2021-03-10 07:49

import content.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0041_auto_20210309_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataimport',
            name='description',
            field=models.TextField(max_length=500000, verbose_name='Description'),
        ),
    ]

# Generated by Django 3.2.4 on 2021-07-23 04:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0035_tender_buyer_protect'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodsservices',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='goodsservices',
            name='supplier',
        ),
    ]
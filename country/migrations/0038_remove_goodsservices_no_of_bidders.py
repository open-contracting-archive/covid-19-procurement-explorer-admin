# Generated by Django 3.2.4 on 2021-08-02 08:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0037_country_covid_active_cases'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goodsservices',
            name='no_of_bidders',
        ),
    ]
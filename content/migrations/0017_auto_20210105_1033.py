# Generated by Django 3.1.2 on 2021-01-05 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0016_auto_20210105_1033"),
    ]

    operations = [
        migrations.AlterField(
            model_name="countrypartner",
            name="order",
            field=models.IntegerField(null=True),
        ),
    ]

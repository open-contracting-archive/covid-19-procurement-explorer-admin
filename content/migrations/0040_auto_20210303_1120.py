# Generated by Django 3.1.2 on 2021-03-03 11:20

import content.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0039_merge_20210302_0515"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataimport",
            name="no_of_rows",
            field=models.CharField(default=0, max_length=10, null=True, verbose_name="No of rows"),
        ),
    ]

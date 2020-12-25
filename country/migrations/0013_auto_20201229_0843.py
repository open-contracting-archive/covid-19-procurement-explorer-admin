# Generated by Django 3.1.2 on 2020-12-29 08:43

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0012_auto_20201225_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equitykeywords',
            name='keyword',
            field=models.CharField(max_length=100, verbose_name='Keyword'),
        ),
        migrations.AlterField(
            model_name='goodsservices',
            name='classification_code',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Classification code'),
        ),
        migrations.AlterField(
            model_name='goodsservicescategory',
            name='category_name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Category name'),
        ),
        migrations.AlterField(
            model_name='tender',
            name='contract_id',
            field=models.CharField(max_length=150, null=True, verbose_name='Contract ID'),
        ),
        migrations.AlterField(
            model_name='tender',
            name='equity_categories',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), default=list, null=True, size=None),
        ),
    ]
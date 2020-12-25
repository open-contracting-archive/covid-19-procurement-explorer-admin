# Generated by Django 3.1.2 on 2020-12-25 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0011_country_continent'),
    ]

    operations = [
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
    ]
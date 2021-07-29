# Generated by Django 3.2.4 on 2021-07-23 04:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0034_auto_20210505_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tender',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tenders', to='country.buyer'),
        ),
        migrations.AlterField(
            model_name='tender',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='tenders', to='country.supplier'),
        ),
    ]

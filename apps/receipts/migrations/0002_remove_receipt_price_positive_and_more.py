# Generated by Django 5.2.4 on 2025-07-23 16:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0001_initial'),
        ('restaurants', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='receipt',
            name='price_positive',
        ),
        migrations.RemoveConstraint(
            model_name='receipt',
            name='image_or_url_required',
        ),
        migrations.AlterField(
            model_name='receipt',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurants.restaurant'),
        ),
    ]

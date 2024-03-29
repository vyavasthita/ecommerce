# Generated by Django 4.2.1 on 2023-05-27 08:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('price', models.PositiveSmallIntegerField(verbose_name=django.core.validators.MinValueValidator(1))),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.collection')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_quantity', models.PositiveSmallIntegerField(verbose_name=django.core.validators.MinValueValidator(0))),
                ('available_quantity', models.PositiveSmallIntegerField(verbose_name=django.core.validators.MinValueValidator(0))),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='store.product')),
            ],
        ),
    ]

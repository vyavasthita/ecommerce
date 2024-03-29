# Generated by Django 4.2.1 on 2023-05-27 08:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_inventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='name',
            field=models.CharField(choices=[('Elec', 'Electronics'), ('Food', 'Food'), ('Fa', 'Fashion'), ('Gro', 'Grocery'), ('Spo', 'Sports'), ('Bo', 'Books'), ('Ent', 'Entertainmaint')], max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='available_quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='total_quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]

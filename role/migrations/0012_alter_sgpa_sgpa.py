# Generated by Django 3.2.3 on 2021-07-13 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('role', '0011_sgpa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sgpa',
            name='sgpa',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]
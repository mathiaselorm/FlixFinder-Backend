# Generated by Django 5.0.4 on 2024-08-17 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='score',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=3),
        ),
    ]

# Generated by Django 2.2.1 on 2019-06-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('animals_server', '0005_auto_20190619_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='points_level',
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
    ]

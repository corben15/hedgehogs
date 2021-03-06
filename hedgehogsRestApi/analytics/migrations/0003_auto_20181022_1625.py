# Generated by Django 2.1.2 on 2018-10-22 20:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_auto_20181022_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='daily_price_info',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='daily_price_info',
            name='week_high_52',
            field=models.FloatField(default=False),
        ),
        migrations.AddField(
            model_name='daily_price_info',
            name='week_low_52',
            field=models.FloatField(default=False),
        ),
    ]

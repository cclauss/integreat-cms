# Generated by Django 3.2.16 on 2023-01-31 18:53

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add stops in the vicinity and spoken languages at a location
    """
    dependencies = [
        ('cms', '0060_user_distribute_sidebar_boxes'),
    ]

    operations = [
        migrations.AddField(
            model_name='poi',
            name='spoken_languages',
            field=models.CharField(blank=True, help_text='List here all languages, that are spoken at the location. Please separate them by comma', max_length=50, verbose_name='Spoken languages'),
        ),
        migrations.AddField(
            model_name='poi',
            name='stops',
            field=models.CharField(blank=True, help_text='List here the stops for public transport in the vicinity. Please separate them by comma', max_length=250, verbose_name='Stops in the vicinity'),
        ),
    ]

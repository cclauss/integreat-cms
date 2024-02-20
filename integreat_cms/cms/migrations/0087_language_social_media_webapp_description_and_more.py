# Generated by Django 4.2.10 on 2024-02-20 15:32

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add social media title and social media description to language model
    """

    dependencies = [
        ("cms", "0086_alter_fields_for_django_4"),
    ]

    operations = [
        migrations.AddField(
            model_name="language",
            name="social_media_webapp_description",
            field=models.TextField(
                blank=True,
                help_text="Displayed description of the WebApp in the search results and on social media pages (max 200 characters).",
                max_length=200,
                verbose_name="Social media description",
            ),
        ),
        migrations.AddField(
            model_name="language",
            name="social_media_webapp_title",
            field=models.CharField(
                default="Integreat",
                help_text="Displayed title of the WebApp in the search results and on social media pages (max 100 characters).",
                max_length=100,
                verbose_name="Social media title of the WebApp",
            ),
        ),
    ]

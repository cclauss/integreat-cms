# Generated by Django 3.2.22 on 2023-10-20 14:37

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add fields required for page based offers
    """

    dependencies = [
        ("cms", "0082_alter_user_expert_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="offertemplate",
            name="supported_by_app_in_content",
            field=models.BooleanField(
                blank=True,
                default=False,
                help_text="Whether the Integreat app supports displaying offers from this provider in pages",
                verbose_name="supported by app in content",
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="embedded_offers",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select an offer provider whose offers should be displayed on this page.",
                related_name="pages",
                to="cms.offertemplate",
                verbose_name="page based offer",
            ),
        ),
    ]
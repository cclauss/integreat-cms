# Generated by Django 3.2.16 on 2023-01-30 13:07

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add setting to toggle the automatic distribution of sidebar boxes
    """

    dependencies = [
        ("cms", "0059_add_poicategory_icon_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="distribute_sidebar_boxes",
            field=models.BooleanField(
                default=False,
                help_text="Enable this option to automatically distribute the boxes in the sidebar of forms to make the best use of screen space. This only affects screen resolutions where the boxes are displayed in two columns.",
                verbose_name="automatically distribute sidebar boxes",
            ),
        ),
    ]
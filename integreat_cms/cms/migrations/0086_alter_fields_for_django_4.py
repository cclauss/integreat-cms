# Generated by Django 4.2.9 on 2024-02-05 08:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Alter fields for update to Django 4.2
    """

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("cms", "0085_rename_review_to_approval"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="icon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cms.mediafile",
                verbose_name="icon",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="cms.poi",
                verbose_name="location",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.region",
                verbose_name="region",
            ),
        ),
        migrations.AlterField(
            model_name="eventtranslation",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="creator",
            ),
        ),
        migrations.AlterField(
            model_name="eventtranslation",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.language",
                verbose_name="language",
            ),
        ),
        migrations.AlterField(
            model_name="feedback",
            name="polymorphic_ctype",
            field=models.ForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="polymorphic_%(app_label)s.%(class)s_set+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="imprintpage",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.region",
                verbose_name="region",
            ),
        ),
        migrations.AlterField(
            model_name="imprintpagetranslation",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="creator",
            ),
        ),
        migrations.AlterField(
            model_name="imprintpagetranslation",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.language",
                verbose_name="language",
            ),
        ),
        migrations.AlterField(
            model_name="languagetreenode",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.region",
                verbose_name="region",
            ),
        ),
        migrations.AlterField(
            model_name="organization",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.region",
                verbose_name="region",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="embedded_offers",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select an offer provider whose offers should be displayed on this page.",
                to="cms.offertemplate",
                verbose_name="page based offer",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="icon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cms.mediafile",
                verbose_name="icon",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                help_text="This allows all members of the organization to edit and publish this page.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cms.organization",
                verbose_name="responsible organization",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.region",
                verbose_name="region",
            ),
        ),
        migrations.AlterField(
            model_name="pagetranslation",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="creator",
            ),
        ),
        migrations.AlterField(
            model_name="pagetranslation",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.language",
                verbose_name="language",
            ),
        ),
        migrations.AlterField(
            model_name="poi",
            name="icon",
            field=models.ForeignKey(
                blank=True,
                help_text="The best results are achieved with images in 16:9 aspect ratio.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cms.mediafile",
                verbose_name="icon",
            ),
        ),
        migrations.AlterField(
            model_name="poi",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.region",
                verbose_name="region",
            ),
        ),
        migrations.AlterField(
            model_name="poitranslation",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="creator",
            ),
        ),
        migrations.AlterField(
            model_name="poitranslation",
            name="language",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="cms.language",
                verbose_name="language",
            ),
        ),
    ]
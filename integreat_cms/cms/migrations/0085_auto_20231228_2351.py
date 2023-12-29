# Generated by Django 3.2.23 on 2023-12-28 23:51

from django.db import migrations, models
import django.db.models.constraints


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0084_add_zammad_forms_as_offers'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='page',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('tree_id', 'lft'), name='unique_lft_tree'),
        ),
        migrations.AddConstraint(
            model_name='page',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('tree_id', 'rgt'), name='unique_rgt_tree'),
        ),
    ]

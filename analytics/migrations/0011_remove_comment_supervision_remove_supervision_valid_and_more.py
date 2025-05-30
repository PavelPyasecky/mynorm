# Generated by Django 5.2 on 2025-05-08 10:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0010_alter_activitystatistics_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="supervision",
        ),
        migrations.RemoveField(
            model_name="supervision",
            name="valid",
        ),
        migrations.AddField(
            model_name="comment",
            name="activity_statistics",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="analytics.activitystatistics",
                verbose_name="activity statistics",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="supervision",
            name="validity",
            field=models.BooleanField(default=True, verbose_name="validity"),
        ),
    ]

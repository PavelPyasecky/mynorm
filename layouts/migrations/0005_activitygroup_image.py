# Generated by Django 5.2 on 2025-05-04 13:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0003_imagegallery_remove_galleryimage_gallery_and_more"),
        (
            "layouts",
            "0004_alter_activity_options_alter_activitygroup_options_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="activitygroup",
            name="image",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activity_group",
                to="gallery.imagegallery",
            ),
        ),
    ]

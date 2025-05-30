# Generated by Django 5.2 on 2025-04-29 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_classifier_code_alter_classifier_id"),
        (
            "users",
            "0005_remove_user_organization_required_for_workers_and_more",
        ),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="user",
            unique_together={("classifier", "organization")},
        ),
    ]

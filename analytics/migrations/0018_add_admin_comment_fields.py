# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0017_supervisioncomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='supervision',
            name='admin_comment',
            field=models.TextField(blank=True, help_text='Admin comment for this supervision', null=True, verbose_name='admin comment'),
        ),
        migrations.AddField(
            model_name='activitystatistics',
            name='admin_comment',
            field=models.TextField(blank=True, help_text='Admin comment for this activity statistics', null=True, verbose_name='admin comment'),
        ),
    ]


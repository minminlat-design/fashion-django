# Generated by Django 5.2 on 2025-05-14 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("variation", "0003_variationoption_included_by_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="variationoption",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="variation_options/%Y/%m/%d/"
            ),
        ),
    ]

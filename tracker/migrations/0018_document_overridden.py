# Generated by Django 4.2.6 on 2023-12-21 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0017_document_file_checked_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='overridden',
            field=models.BooleanField(default=False),
        ),
    ]

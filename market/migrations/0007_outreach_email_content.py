# Generated by Django 4.2.6 on 2024-01-26 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0006_remove_outreach_title_outreach_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='outreach',
            name='email_content',
            field=models.TextField(blank=True, null=True),
        ),
    ]

# Generated by Django 4.2.6 on 2024-02-08 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prospect', '0009_prospect_context'),
    ]

    operations = [
        migrations.AddField(
            model_name='prospect',
            name='client_onboarded',
            field=models.BooleanField(default=False),
        ),
    ]

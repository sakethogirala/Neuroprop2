# Generated by Django 4.1 on 2022-12-22 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_rename_referrer_referral_recipient_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_uid',
            new_name='uid',
        ),
    ]

# Generated by Django 4.1 on 2022-10-04 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_accountlink_linked_alter_accountlink_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]

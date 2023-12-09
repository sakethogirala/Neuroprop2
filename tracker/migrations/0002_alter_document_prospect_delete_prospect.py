# Generated by Django 4.2.6 on 2023-11-10 00:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prospect', '0002_address_prospect'),
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='prospect',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prospect.prospect'),
        ),
        migrations.DeleteModel(
            name='Prospect',
        ),
    ]

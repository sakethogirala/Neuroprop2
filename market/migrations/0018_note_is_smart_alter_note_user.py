# Generated by Django 4.2.6 on 2024-02-20 04:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0017_alter_outreach_email_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='is_smart',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='note',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL),
        ),
    ]

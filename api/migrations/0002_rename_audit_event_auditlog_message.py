# Generated by Django 3.2.16 on 2023-05-09 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auditlog',
            old_name='audit_event',
            new_name='message',
        ),
    ]
# Generated by Django 3.2.16 on 2023-05-09 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_auditlog_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]

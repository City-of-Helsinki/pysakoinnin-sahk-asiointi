# Generated by Django 3.2.16 on 2023-05-09 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20230509_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='id',
            field=models.IntegerField(default=1, primary_key=True, serialize=False),
        ),
    ]

# Generated by Django 5.0.6 on 2024-06-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutee',
            name='info',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='experience',
            field=models.TextField(),
        ),
    ]

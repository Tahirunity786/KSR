# Generated by Django 5.0.6 on 2024-06-10 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_accounts', '0006_rename_response_time_user_response_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, db_index=True, max_length=200, null=True),
        ),
    ]

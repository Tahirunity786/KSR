# Generated by Django 5.0.6 on 2024-06-14 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_accounts', '0007_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_provider',
            field=models.CharField(db_index=True, default=None, max_length=50, null=True),
        ),
    ]
# Generated by Django 5.0.6 on 2024-06-07 18:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_accounts', '0002_alter_tutee_info_alter_tutor_experience'),
        ('core_jobs', '0005_alter_job_tutor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='tutor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core_accounts.tutor'),
        ),
    ]
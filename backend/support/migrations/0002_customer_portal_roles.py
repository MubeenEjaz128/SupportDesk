import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('supervisor', 'Supervisor'),
                    ('agent', 'Agent'),
                    ('customer', 'Customer'),
                ],
                default='agent',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='agentprofile',
            name='customer',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='portal_profile',
                to='support.customer',
            ),
        ),
    ]

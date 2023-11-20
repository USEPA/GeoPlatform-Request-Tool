# Generated by Django 4.1.9 on 2023-06-16 15:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0027_agol_allow_external_accounts_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agol',
            name='allow_external_accounts',
            field=models.BooleanField(default=False, help_text='Allow external (non-enterprise) accounts to be created.'),
        ),
        migrations.AlterField(
            model_name='agol',
            name='enterprise_precreate_domains',
            field=models.TextField(blank=True, help_text='Separate email domains with comma (e.g. gmail.com,hotmail.com). Value required if external account creation is not allowed', null=True, verbose_name='Email domains for enterprise accounts'),
        ),
        migrations.AlterField(
            model_name='responseproject',
            name='authoritative_group',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_auth_group': True}, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.agolgroup', verbose_name='Authoritative Group'),
        ),
        migrations.AlterField(
            model_name='responseproject',
            name='requester',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='requested_responses', to=settings.AUTH_USER_MODEL),
        ),
    ]

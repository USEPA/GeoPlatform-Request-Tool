# Generated by Django 4.1.9 on 2023-06-06 21:32

from django.db import migrations, models
import django.db.models.deletion


def copy_roles(apps, schema_editor):
    TempAGOLRole = apps.get_model('accounts', 'TempAGOLRole')
    AGOLRole = apps.get_model('accounts', 'AGOLRole')
    for r in AGOLRole.objects.all():
        t = TempAGOLRole.objects.create(
            role_id=r.id,
            name=r.name,
            description=r.description,
            is_available=r.is_available,
            agol=r.agol,
            system_default=r.system_default
        )
        r.responses.update(temp_role=t)
        r.account_requests.update(temp_role=t)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0024_alter_agol_user_alter_agoluserfields_portal_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempAGOLRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_id', models.CharField(max_length=16)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('is_available', models.BooleanField(default=False)),
                ('system_default', models.BooleanField(default=False)),
                ('agol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles_temp',
                                           to='accounts.agol')),
            ],
        ),
        migrations.AddField(
            model_name='accountrequests',
            name='temp_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='accounts.tempagolrole'),
        ),
        migrations.AddField(
            model_name='responseproject',
            name='temp_role',
            field=models.ForeignKey(blank=True, help_text='System default will be used if left blank.',
                                    limit_choices_to={'is_available': True}, null=True,
                                    on_delete=django.db.models.deletion.PROTECT, to='accounts.tempagolrole',
                                    verbose_name='Role'),
        ),
        migrations.AlterField(
            model_name='accountrequests',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    related_name='account_requests', to='accounts.agolrole'),
        ),
        migrations.AlterField(
            model_name='responseproject',
            name='role',
            field=models.ForeignKey(blank=True, help_text='System default will be used if left blank.',
                                    limit_choices_to={'is_available': True}, null=True,
                                    on_delete=django.db.models.deletion.PROTECT, related_name='responses',
                                    to='accounts.agolrole', verbose_name='Role'),
        ),
        migrations.RunPython(copy_roles, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='accountrequests',
            name='role',
        ),
        migrations.RemoveField(
            model_name='responseproject',
            name='role',
        ),
        migrations.DeleteModel(
            name='AGOLRole',
        ),
        migrations.RenameModel('TempAGOLRole', 'AGOLRole'),
        migrations.RenameField(model_name='responseproject', old_name='temp_role', new_name='role'),
        migrations.RenameField(model_name='accountrequests', old_name='temp_role', new_name='role')
    ]

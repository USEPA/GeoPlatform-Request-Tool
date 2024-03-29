# Generated by Django 2.2.24 on 2021-12-06 21:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_requesters(apps, schema_editor):
    ResponseProject = apps.get_model('accounts', 'ResponseProject')
    for r in ResponseProject.objects.all():
        r.requester = r.users.first()
        r.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0013_auto_20211203_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='responseproject',
            name='requester',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='requested_responses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(set_requesters, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='responseproject',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requested_responses',
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]

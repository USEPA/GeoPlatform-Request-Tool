# Generated by Django 2.2.7 on 2019-12-10 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20191209_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountrequests',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='accountrequests',
            name='reason',
            field=models.CharField(choices=[('Emergency Response', 'Emergency Response'), ('Other Federal Agency', 'Other Federal Agency'), ('State Agency', 'State Agency'), ('University', 'University'), ('Long Term GIS Support', 'Long Term GIS Support'), ('Non Government Organization', 'Non Government Organization'), ('Tribal Government', 'Tribal Government'), ('Citizen Advisor', 'Citizen Advisor'), ('Other', 'Other')], default='Emergency Response', max_length=200),
        ),
    ]
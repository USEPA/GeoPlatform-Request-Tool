# Generated by Django 4.2.16 on 2025-01-07 18:24

from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0033_agolgroup_users_groupmembership_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agol',
            name='email_signature_content',
            field=django_ckeditor_5.fields.CKEditor5Field(default='''<p>
    A few important points:
</p>
<ul>
    <li>
        The EPA {{ PORTAL }} is a place for <i>creating and sharing maps and map applications</i>. Depending on your access level, you may only be able to view content items, or you may be able to collaborate by creating and editing items.
    </li>
    <li>
        Multi-Factor Authentication (MFA) is now required to be enabled on all accounts per <a href="https://www.epa.gov/system/files/documents/2021-09/information_security_identification_and_authentication_procedure.pdf">security policy</a>. Guidance for the simple process of enabling two-factor authentication can be found in <a href="https://epa.maps.arcgis.com/sharing/rest/content/items/079ede9b32464c73815d386703d3f88b/data">this document</a>. You will have a short grace period following account creation to enable MFA, after which your account will be automatically disabled.
    </li>
    <li>
        If you do something with the {{ PORTAL }} that <i>you would like to share</i> with our community, please contact us and let us know! The best contact is this email address: <a href="mailto:GeoServices@epa.gov">GeoServices@epa.gov</a>.
    </li>
    <li>
        Discover additional data resources by visiting the <a href="https://edg.epa.gov/">Environmental Dataset Gateway</a> or contacting <a href="mailto:edg@epa.gov">edg@epa.gov</a>
    </li>
    <li>
        We hope that you enjoy using this platform to build and enhance your mapping capabilities, but we also have one major rule to consider as you use the {{ PORTAL }}:<br>
        <span style="color:red;"><strong>No PERSONALLY IDENTIFIABLE INFORMATION (PII) or National Security Information (NSI) can be stored on the {{ PORTAL }}.</strong>&nbsp;</span><br>
        If you need a place for storing names, social security numbers, phone numbers, home addresses and the like – PLEASE do not store them here. PII or NSI found in the {{ PORTAL }}, whether added inadvertently or intentionally, will be removed.
    </li>
</ul>
<p>
    Thank you for your attention to this important information and welcome again to the {{ PORTAL }} community.<br>
    <br>
    The {{ PORTAL }} Administration
</p>
<hr>'''),
            preserve_default=False,
        ),
    ]

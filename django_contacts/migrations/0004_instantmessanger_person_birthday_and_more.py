# Generated by Django 5.1.2 on 2024-11-01 13:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_contacts', '0003_googleaccount_api_call_counter'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstantMessanger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('im_type', models.CharField(choices=[('skype', 'Skype'), ('icq', 'ICQ')], max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='PersonCompanyConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_contacts.company')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_contacts.person')),
                ('usage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_contacts.usagecategory')),
            ],
        ),
        migrations.CreateModel(
            name='PersonIMConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('im', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_contacts.instantmessanger')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_contacts.person')),
                ('usage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_contacts.usagecategory')),
            ],
        ),
    ]
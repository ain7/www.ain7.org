# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-30 23:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('annuaire', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Travel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change_at', models.DateTimeField(blank=True, editable=False, verbose_name='Modifi\xe9 pour la derni\xe8re fois \xe0')),
                ('label', models.CharField(max_length=50, verbose_name='libell\xe9')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Date de d\xe9but')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Date de fin')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('price', models.IntegerField(blank=True, null=True, verbose_name='prix')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to=b'data', verbose_name='vignette')),
                ('report', models.TextField(blank=True, null=True, verbose_name='compte rendu')),
                ('last_change_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_changed_travel', to='annuaire.Person', verbose_name='Auteur de la derni\xe8re modification')),
            ],
            options={
                'ordering': ['-start_date', '-end_date'],
                'verbose_name': 'voyage',
            },
        ),
        migrations.CreateModel(
            name='TravelType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50, verbose_name='type')),
            ],
            options={
                'verbose_name': 'type de voyage',
                'verbose_name_plural': 'types de voyage',
            },
        ),
        migrations.AddField(
            model_name='travel',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voyages.TravelType', verbose_name='type'),
        ),
    ]
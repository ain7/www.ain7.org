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
            name='LostPassword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annuaire.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change_at', models.DateTimeField(blank=True, editable=False, verbose_name='Modifi\xe9 pour la derni\xe8re fois \xe0')),
                ('lang', models.CharField(default=b'fr', max_length=10, verbose_name='langue')),
                ('title', models.CharField(max_length=150, verbose_name='titre')),
                ('body', models.TextField(blank=True, null=True, verbose_name='corps')),
                ('last_change_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_changed_text', to='annuaire.Person', verbose_name='Auteur de la derni\xe8re modification')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TextBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_change_at', models.DateTimeField(blank=True, editable=False, verbose_name='Modifi\xe9 pour la derni\xe8re fois \xe0')),
                ('shortname', models.CharField(max_length=50, verbose_name='identifiant')),
                ('url', models.CharField(blank=True, max_length=100, null=True, verbose_name='url')),
                ('last_change_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_changed_textblock', to='annuaire.Person', verbose_name='Auteur de la derni\xe8re modification')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='text',
            name='textblock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.TextBlock'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import leaflet_storage.models
import django.db.models.deletion
from django.conf import settings
import leaflet_storage.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataLayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('geojson', models.FileField(null=True, upload_to=leaflet_storage.models.upload_to, blank=True)),
                ('display_on_load', models.BooleanField(default=False, help_text='Display this layer on load.', verbose_name='display on load')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('details', models.URLField(help_text='Link to a page where the licence is detailed.', verbose_name='details')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('slug', models.SlugField()),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('center', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='center', geography=True)),
                ('zoom', models.IntegerField(default=7, verbose_name='zoom')),
                ('locate', models.BooleanField(default=False, help_text='Locate user on load?', verbose_name='locate')),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('edit_status', models.SmallIntegerField(default=3, verbose_name='edit status', choices=[(1, 'Everyone can edit'), (2, 'Only editors can edit'), (3, 'Only owner can edit')])),
                ('share_status', models.SmallIntegerField(default=1, verbose_name='share status', choices=[(1, 'everyone (public)'), (2, 'anyone with link'), (3, 'editors only')])),
                ('settings', leaflet_storage.fields.DictField(null=True, verbose_name='settings', blank=True)),
                ('editors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='editors', blank=True)),
                ('licence', models.ForeignKey(on_delete=django.db.models.deletion.SET_DEFAULT, default=leaflet_storage.models.get_default_licence, verbose_name='licence', to='leaflet_storage.Licence', help_text='Choose the map licence.')),
                ('owner', models.ForeignKey(related_name='owned_maps', verbose_name='owner', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pictogram',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('attribution', models.CharField(max_length=300)),
                ('pictogram', models.ImageField(upload_to=b'pictogram')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TileLayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('url_template', models.CharField(help_text='URL template using OSM tile format', max_length=200)),
                ('minZoom', models.IntegerField(default=0)),
                ('maxZoom', models.IntegerField(default=18)),
                ('attribution', models.CharField(max_length=300)),
                ('rank', models.SmallIntegerField(help_text='Order of the tilelayers in the edit box', null=True, blank=True)),
            ],
            options={
                'ordering': ('rank', 'name'),
            },
        ),
        migrations.AddField(
            model_name='map',
            name='tilelayer',
            field=models.ForeignKey(related_name='maps', verbose_name='background', blank=True, to='leaflet_storage.TileLayer', null=True, on_delete=django.db.models.deletion.SET_DEFAULT),
        ),
        migrations.AddField(
            model_name='datalayer',
            name='map',
            field=models.ForeignKey(to='leaflet_storage.Map', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]

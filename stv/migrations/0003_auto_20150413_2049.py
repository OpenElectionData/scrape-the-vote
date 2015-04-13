# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stv', '0002_auto_20150413_2015'),
    ]

    operations = [
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('election_name', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='ElectionReport',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('image', models.FileField(upload_to='')),
                ('hash', models.CharField(max_length=1000, unique=True)),
                ('url', models.URLField()),
                ('first_seen', models.DateTimeField()),
                ('last_seen', models.DateTimeField()),
                ('election', models.ForeignKey(to='stv.Election')),
            ],
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]

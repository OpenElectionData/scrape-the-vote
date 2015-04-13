# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stv', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='first_seen',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 13, 20, 15, 16, 301848, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='image',
            field=models.FileField(default='', upload_to=b''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='image_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='last_seen',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 13, 20, 15, 35, 130182, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

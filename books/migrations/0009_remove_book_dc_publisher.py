# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_auto_20160225_1838'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='dc_publisher',
        ),
    ]

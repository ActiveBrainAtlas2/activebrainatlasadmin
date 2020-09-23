# Generated by Django 3.0.3 on 2020-09-21 12:19

import cvat.apps.git.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('engine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitData',
            fields=[
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='engine.Task')),
                ('url', models.URLField(max_length=2000)),
                ('path', models.CharField(max_length=256)),
                ('sync_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=cvat.apps.git.models.GitStatusChoice['NON_SYNCED'], max_length=20)),
                ('lfs', models.BooleanField(default=True)),
            ],
        ),
    ]

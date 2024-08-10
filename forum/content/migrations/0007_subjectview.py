# Generated by Django 4.1 on 2024-08-05 07:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_remove_message_updated_content_created_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime(2024, 8, 5, 7, 23, 15, 961104, tzinfo=datetime.timezone.utc))),
                ('views', models.PositiveSmallIntegerField()),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='content.subject')),
            ],
            options={
                'ordering': ['date'],
                'unique_together': {('subject', 'date')},
            },
        ),
    ]

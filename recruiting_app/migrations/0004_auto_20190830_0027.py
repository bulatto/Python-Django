# Generated by Django 2.2.4 on 2019-08-29 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruiting_app', '0003_auto_20190830_0015'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='answer',
            new_name='correctAnswer',
        ),
    ]

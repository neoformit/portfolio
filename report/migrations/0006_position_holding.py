# Generated by Django 3.0.7 on 2020-06-07 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0005_auto_20200607_0154'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='holding',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]

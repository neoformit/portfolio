# Generated by Django 3.0.7 on 2020-06-10 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_auto_20200609_0746'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='currency',
            field=models.CharField(default='USD', max_length=10),
        ),
    ]

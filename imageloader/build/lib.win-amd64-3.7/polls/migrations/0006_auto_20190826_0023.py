# Generated by Django 2.2.4 on 2019-08-25 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_uploadfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadfile',
            name='file',
            field=models.FileField(upload_to='pic'),
        ),
    ]
